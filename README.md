# atime-test

This is a simple test to compare various ways of getting the atime of directories and files.

Example output:

```
> python playground.py
Running print_atimes_scandir on /tmp/test_root
First run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Second run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Sun Dec  1 19:59:44 2024'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Results are different!

Running print_atimes_listdir on /tmp/test_root
First run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Second run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Results are the same!

Running print_atimes_scandir_with_fd on /tmp/test_root
First run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Second run:
[('/tmp/test_root/file1.txt', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir', 'Fri Dec  2 16:53:20 2022'), ('/tmp/test_root/subdir/file2.txt', 'Fri Dec  2 16:53:20 2022')]
Results are the same!
```