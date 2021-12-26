# Parallel File Downloader CLI App
CLI application downloads an index file to obtain a list of text file URLs and download these files in parallel by multi-threading.

- If the requested file is found in the server, the response is a 200 OK message.  When this is the case, our program establishes <connection_count> parallel connections with the server including the file, downloads non-overlapping parts of the file through these connections, constructs and saves the file under the directory in which our program runs


- Tested on Unix/Linux and Mac machines. 

## Test URLs:
  * www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
  * www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt

## Run with just Index file:
```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt
```

```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt
```

## Run with Index file and Number of Parellel Connections:
```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt 3
```

```
python ParallelFileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt 5
```
