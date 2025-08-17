import os
import logging

def inc_count(count_path):
    if not os.path.exists(count_path):
        with open(count_path, "w") as f:
            f.write("1")
        return 1
    with open(count_path, "r+") as f:
        count = int(f.read())
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    logging.info(f"lock count {count}")
    return count

def dec_count(count_path):
    if not os.path.exists(count_path):
        return 0
    with open(count_path, "r+") as f:
        count = int(f.read())
        count -= 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    logging.info(f"lock count {count}")
    return count