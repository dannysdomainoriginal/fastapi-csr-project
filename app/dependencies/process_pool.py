from concurrent.futures import ProcessPoolExecutor

pool = ProcessPoolExecutor(max_workers=4)


def get_process_pool():
    return pool
