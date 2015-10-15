# rsall

A (backup) program to rsync a list of local filesystem trees on a mac to destinations on multiple external drives mounted on the mac.

## Wake Up Call

External drives may be sleeping and need to be spun up.  So we write a random file to the mountpoint directory, fsync() the file, and delete it.  We call this waking up the drive.  We do this before rsync'ing to the drive to avoid an I/O error.

We keep track of the state of each rsync command (command itself, status, stdout, stderr), and if any has a problem, we report this state at the end of the run.
