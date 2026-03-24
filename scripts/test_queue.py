import sys
import time

from redis import Redis
from rq import Queue, Retry

sys.path.insert(0, ".")

from app import config
from app.models.task import Task, get_task, save_task
from app.tasks import generate_audiobook


def main():
    conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    queue = Queue("audiobook", connection=conn, default_timeout=config.JOB_TIMEOUT)

    filename = sys.argv[1] if len(sys.argv) > 1 else "test.txt"
    language = sys.argv[2] if len(sys.argv) > 2 else "eng"

    task = Task.new(filename=filename, language=language)
    save_task(task)

    print(f"Created task {task.task_id}: file={filename}, lang={language}, status={task.status}")

    job = queue.enqueue(
        generate_audiobook,
        task_id=task.task_id,
        filename=filename,
        language=language,
        retry=Retry(max=2, interval=[30, 60]),
        job_timeout=config.JOB_TIMEOUT,
    )

    print(f"Job ID: {job.id}")

    print("\nWaiting for completion...")
    while True:
        current = get_task(task.task_id)
        status = current.status if current else "unknown"
        print(f"  [{task.task_id}] status={status}")

        if status in ("done", "error"):
            break
        time.sleep(5)

    if current and status == "done":
        print(f"\nDone in {current.elapsed:.1f}s")
        print(f"Output: {current.output_files}")
    elif current and status == "error":
        print(f"\nError: {current.error}")


if __name__ == "__main__":
    main()
