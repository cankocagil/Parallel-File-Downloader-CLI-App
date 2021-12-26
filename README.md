# Parallel File Downloader CLI App
Tested on Unix/Linux and Mac machines. 

## Test URLs:
www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt

## Run with just Index file:
```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
```

or 

```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt
```

## Run with Index file and Number of Parellel Connections:
```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt 3
```
or

```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt 5
```