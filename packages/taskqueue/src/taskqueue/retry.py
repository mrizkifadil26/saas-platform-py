def compute_delay_seconds(attempt: int, base_delay: float = 2.0, max_delay: float = 300.0) -> float:
    """
    Compute the delay in seconds before the next retry attempt using exponential backoff.

    :param attempt: The current attempt number (0-based).
    :param base_delay: The base delay in seconds.
    :param max_delay: The maximum delay in seconds.
    :return: The computed delay in seconds.
    """
    delay = base_delay * (2**attempt)
    return min(delay, max_delay)


def should_bury(retries: int, max_retries: int) -> bool:
    """
    Determine whether a job should be buried based on its retry count.

    :param retries: The number of times the job has been retried.
    :param max_retries: The maximum number of retries allowed for the job.
    :return: True if the job should be buried, False otherwise.
    """
    return retries >= max_retries
