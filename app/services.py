from datetime import datetime, timezone, timedelta
from concurrent.futures import ProcessPoolExecutor

from jose import jwt, JWTError
from fastapi import HTTPException
from asyncio import to_thread, get_running_loop, gather

from uuid import UUID
from app.config.settings import settings

from app.config.database import User
from app.repositories import BlogRepo, UserRepo, IssueRepo
from app.schemas import (
    BlogCreate,
    BlogUpdate,
    UserCreate,
    UserLogin,
    UserUpdate,
    IssueCreate,
    IssueUpdate,
)


# ---------------------------------------------------------------------------- #
#                                 JWT Handling                                 #
# ---------------------------------------------------------------------------- #
class TokenService:
    SECRET_KEY = settings.secret_key
    ALGORITHM = "HS256"

    @classmethod
    def issue_token(
        cls, user_id: UUID, expires_delta: timedelta = timedelta(days=7)
    ) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + expires_delta,
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> UUID:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id: str | None = payload.get("sub")

            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            return UUID(user_id)
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Token verification failed",
            )


# ---------------------------------------------------------------------------- #
#                                 BLOG SERVICE                                 #
# ---------------------------------------------------------------------------- #
class BlogService:
    def __init__(self, repo: BlogRepo, pool: ProcessPoolExecutor) -> None:
        self.repo = repo
        self.pool = pool

    async def get_all_posts(
        self,
        limit: int = 10,
        skip: int = 0,
    ):
        return await self.repo.get_all_posts(limit, skip)

    async def create_post(self, fields: BlogCreate):
        return await self.repo.create_post(post=fields)

    async def get_post_or_404(self, id: UUID):
        post = await self.repo.get_post_by_id(id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return post

    async def update_post_or_404(self, id: UUID, fields: BlogUpdate):
        post = await self.get_post_or_404(id)
        return await self.repo.update_post(post, fields)

    async def delete_post_or_404(self, id: UUID):
        deleted = await self.repo.delete_post(id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def _score(q: str, content: str) -> int:
        return content.lower().count(q.lower())

    # ---------------------------------------------------------------------------- #
    #                           SEARCH POSTS USING THREAD                          #
    # ---------------------------------------------------------------------------- #
    async def search_posts_using_thread(self, query: str, posts):
        posts = await self.repo.get_all_posts()

        results = []
        for post in posts:
            score = await to_thread(self._score, query, post.content)
            results.append((score, post))

        results.sort(reverse=True, key=lambda x: x[0])
        return [post for _, post in results]

    # ---------------------------------------------------------------------------- #
    #                            SEARCH POSTS USING POOL                           #
    # ---------------------------------------------------------------------------- #
    async def search_posts_using_pool(self, query: str, posts):
        posts = await self.repo.get_all_posts()
        loop = get_running_loop()

        # Prepare lightweight payloads (IMPORTANT for multiprocessing)
        tasks: list[tuple[str, str]] = [(query, post.content) for post in posts]

        # Run CPU work in process pool
        futures = [
            loop.run_in_executor(self.pool, self._score, q, content)
            for q, content in tasks
        ]
        scores = await gather(*futures)

        # Combine results safely
        results = list(zip(scores, posts))
        results.sort(key=lambda x: x[0], reverse=True)
        return [post for _, post in results]

    @staticmethod
    def _score_batch(q: str, contents: list[str]) -> list[int]:
        return [c.lower().count(q.lower()) for c in contents]

    # ---------------------------------------------------------------------------- #
    #                            SEARCH POSTS IN CHUNKS                            #
    # ---------------------------------------------------------------------------- #
    async def search_posts_in_chunks(self, query: str, posts):
        loop = get_running_loop()

        def _chunk(data, size: int):
            for i in range(0, len(data), size):
                yield data[i : i + size]

        CHUNK_SIZE = 100
        chunks = list(_chunk(posts, CHUNK_SIZE))

        futures = []
        for chunk in chunks:
            contents = [post.content for post in chunk]
            futures.append(
                loop.run_in_executor(self.pool, self._score_batch, query, contents)
            )

        chunk_scores = await gather(*futures)
        results = []

        for chunk, scores in zip(chunks, chunk_scores):
            for post, score in zip(chunk, scores):
                results.append((score, post))

        results.sort(key=lambda x: x[0], reverse=True)
        return [post for _, post in results]

    # ---------------------------------------------------------------------------- #
    #                                 SEARCH POSTS                                 #
    # ---------------------------------------------------------------------------- #
    async def search_posts(self, query: str) -> list:
        posts = await self.repo.get_all_posts()
        n = len(posts)

        match n:
            case n if n <= 200:
                return await self.search_posts_using_thread(query, posts=posts)
            case n if n <= 5_000:
                return await self.search_posts_using_pool(query, posts=posts)
            case _:
                return await self.search_posts_in_chunks(query, posts=posts)


# ---------------------------------------------------------------------------- #
#                                 AUTH SERVICE                                 #
# ---------------------------------------------------------------------------- #
class AuthService:
    def __init__(self, repo: UserRepo) -> None:
        self.repo = repo
        self.jwt = TokenService

    async def signup(self, fields: UserCreate):
        exists = await self.repo.get_by_email(fields.email)
        if exists:
            raise HTTPException(400, "Email already registered")

        user = await self.repo.create(fields)
        return self.jwt.issue_token(user.id)

    async def login(self, fields: UserLogin):
        user = await self.repo.get_by_email(fields.email)

        if not user or not user.verify_password(fields.password):
            raise HTTPException(401, "Invalid credentials")

        return self.jwt.issue_token(user.id)


# ---------------------------------------------------------------------------- #
#                                 USER SERVICE                                 #
# ---------------------------------------------------------------------------- #
class UserService:
    def __init__(self, repo: UserRepo, user: User) -> None:
        self.repo = repo
        self.user = user
        self.jwt = TokenService

    def issue_token(self):
        return self.jwt.issue_token(self.user.id)

    async def update_profile(self, fields: UserUpdate):
        return await self.repo.update_profile(self.user, fields)

    async def delete_account(self):
        return await self.repo.delete_profile(self.user)


# ---------------------------------------------------------------------------- #
#                                ISSUES SERVICE                                #
# ---------------------------------------------------------------------------- #
class IssueService:
    def __init__(self, repo: IssueRepo) -> None:
        self.repo = repo

    async def get_all_issues(
        self,
        limit: int = 10,
        skip: int = 0,
    ):
        return await self.repo.get_all_issues(limit, skip)

    async def create_issue(self, fields: IssueCreate):
        return await self.repo.create_issue(issue=fields)

    async def get_issue_or_404(self, id: UUID):
        issue = await self.repo.get_issue_by_id(id)

        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        return issue

    async def update_issue_or_404(self, id: UUID, fields: IssueUpdate):
        issue = await self.get_issue_or_404(id)
        return await self.repo.update_issue(issue, fields)

    async def delete_issue_or_404(self, id: UUID):
        deleted = await self.repo.delete_issue(id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Issue not found")
