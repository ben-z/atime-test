# %%
import os
import time

# %% MARK: utils

def set_times(path, atime=None, mtime=None):
    """
    Set atime and mtime recursively on files and directories.

    :param path: Path to the directory or file
    :param atime: Access time (timestamp), defaults to current time if None
    :param mtime: Modification time (timestamp), defaults to current time if None

    :note: Derived from https://chatgpt.com/share/674cc769-85c8-8010-9f58-29a393814484
    """
    if atime is None or mtime is None:
        current_time = time.time()
        atime = atime or current_time
        mtime = mtime or current_time

    for root, dirs, files in os.walk(path, topdown=False):
        # Set times for files
        for file in files:
            full_path = os.path.join(root, file)
            os.utime(full_path, (atime, mtime))

        # Set times for directories
        for dir in dirs:
            full_path = os.path.join(root, dir)
            os.utime(full_path, (atime, mtime))

    # Set times for the root directory itself
    os.utime(path, (atime, mtime))

def set_up_env(test_root):
    """
    Create files and directories in the test_root directory and set custom atime and mtime.

    :note: Derived from https://chatgpt.com/share/674cc769-85c8-8010-9f58-29a393814484
    """

    if os.path.exists(test_root):
        import shutil
        shutil.rmtree(test_root)

    os.makedirs(test_root, exist_ok=True)

    # Create files and directories
    with open(os.path.join(test_root, "file1.txt"), "w") as f:
        f.write("Test content for file1.")

    subdir = os.path.join(test_root, "subdir")
    os.makedirs(subdir, exist_ok=True)
    with open(os.path.join(subdir, "file2.txt"), "w") as f:
        f.write("Test content for file2.")

    # Set custom atime and mtime
    custom_atime = 1670000000  # Example custom atime
    custom_mtime = 1670000000  # Example custom mtime
    set_times(
        test_root, atime=custom_atime, mtime=custom_mtime
    )

# %% MARK: Print atimes with scandir

def print_atimes_scandir(directory):
    """
    Iterates over a directory and prints the access time (atime) of each file and directory
    without updating their `atime`.

    :param directory: Path to the directory to scan.

    :note: This function uses `os.scandir` to iterate over the directory entries. According to the [Python docs](https://docs.python.org/3/library/os.html#os.scandir), the `os.scandir` uses [`opendir`](https://man7.org/linux/man-pages/man3/opendir.3.html) under the hood. This may restrict the flexibility of the `os.scandir` because e.g. `opendir` doesn't appear to provide a way to set custom flags like `O_NOATIME` to avoid updating the access time of the directory when listing its contents.
    :note: Derived from https://chatgpt.com/share/674cc769-85c8-8010-9f58-29a393814484
    """
    results = []
    for entry in os.scandir(directory):
        # Use low-level file descriptor access
        fd = os.open(entry.path, os.O_RDONLY | os.O_NOATIME)
        stats = os.fstat(fd)
        os.close(fd)
        results.append((entry.path, time.ctime(stats.st_atime)))

        if entry.is_dir(follow_symlinks=False):
            results.extend(print_atimes_scandir(entry.path))
    return results

test_root = "/tmp/test_root"
print(f"Running print_atimes_scandir on {test_root}")
set_up_env(test_root)

print("First run:")
first = print_atimes_scandir(test_root)
print(first)

print("Second run:")
second = print_atimes_scandir(test_root)
print(second)

if first == second:
    print("Results are the same!")
else:
    print("Results are different!")
print()


# %% MARK: Print atimes with listdir

def print_atimes_listdir(directory):
    """
    Iterates over a directory and prints the access time (atime) of each file and directory
    without updating their `atime`.

    :param directory: Path to the directory to scan.

    :note: This function uses `os.listdir` to iterate over the directory entries. It appears that if we pass in an open file descriptor to `os.listdir`, the `os.listdir` function will use the fd as-is using `fdopendir`: https://github.com/python/cpython/blob/04673d2f14414fce7a2372de3048190f66488e6e/Modules/posixmodule.c#L4506-L4517
    The effect of this is that the `os.listdir` function can be configured (using os.O_NOATIME) to not update the access time of the directory itself when listing its contents.
    """
    results = []
    dirfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOATIME)

    for entry in os.listdir(dirfd):
        entry_path = os.path.join(directory, entry)
        # Use low-level file descriptor access
        fd = os.open(entry_path, os.O_RDONLY | os.O_NOATIME)
        stats = os.fstat(fd)
        os.close(fd)
        results.append((entry_path, time.ctime(stats.st_atime)))

        # Recursively scan directories
        if os.path.isdir(entry_path) and not os.path.islink(entry_path):
            results.extend(print_atimes_listdir(entry_path))
    return results

test_root = "/tmp/test_root"
print(f"Running print_atimes_listdir on {test_root}")
set_up_env(test_root)

print("First run:")
first = print_atimes_listdir(test_root)
print(first)

print("Second run:")
second = print_atimes_listdir(test_root)
print(second)

if first == second:
    print("Results are the same!")
else:
    print("Results are different!")
print()

# %% MARK: Print atimes with scandir by passing in file descriptors

def print_atimes_scandir_with_fd(directory):
    """
    Iterates over a directory and prints the access time (atime) of each file and directory
    without updating their `atime`.

    :param directory: Path to the directory to scan.

    :note: This function uses `os.scandir` to iterate over the directory entries. It appears that `os.scandir` can also take in a file descriptor to the directory, just like `os.listdir`. This allows us to avoid updating the access time of the directory itself when listing its contents.
    """
    results = []
    dirfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOATIME)

    for entry in os.scandir(dirfd):
        entry_path = os.path.join(directory, entry.path)
        # Use low-level file descriptor access
        fd = os.open(entry_path, os.O_RDONLY | os.O_NOATIME)
        stats = os.fstat(fd)
        os.close(fd)
        results.append((entry_path, time.ctime(stats.st_atime)))

        if entry.is_dir(follow_symlinks=False):
            results.extend(print_atimes_scandir_with_fd(entry_path))
    return results

test_root = "/tmp/test_root"
print(f"Running print_atimes_scandir_with_fd on {test_root}")
set_up_env(test_root)

print("First run:")
first = print_atimes_scandir_with_fd(test_root)
print(first)

print("Second run:")
second = print_atimes_scandir_with_fd(test_root)
print(second)

if first == second:
    print("Results are the same!")
else:
    print("Results are different!")
print()
