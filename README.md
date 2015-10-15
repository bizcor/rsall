# rsall

A (backup) program to rsync local filesystem trees on a mac to destinations on multiple external drives mounted on the mac.  That is, for each "source tree" we create multiple copies of it, each on a different external drive.

## Wake Up Call

The external drives may be sleeping and need to be woken up.  In order to wake up a drive, we write a random file to its mountpoint directory, sync the file to disk, and delete the file.  We do this for all listed drives before rsync'ing to avoid an I/O error from the operating system.

We keep track of the state of each rsync command (the command and its args, and its status, stdout, and stderr), and if any command has a problem, we report its state at the end of the run.
