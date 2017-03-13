# asparser-python
Analysis parser - Iteration1

This is a script which extracts and reads all the log and text files 
to list the errors and warnings in the logs along with some configuration details from the AppInternals 10 appliance.

The script generates 2 output files after it finishes running and leaves the extracted bundle files/folders. 
The 2 output files will be named - errorsandwarns.txt and analysisserverdetails.txt.

Steps on running the script:

Install Python 2.7 or higher or place the script where you have python installed Run the script and it enter the location of the system dump from AppInternals 10 appliance.
The script will unzip the sysdump in the same location where you placed the script. 
The script will also create the 2 output files mentioned above in the same location where the script is located.

NOTE:

--Please use script in python2 if you are running python version 2.7 or higher but lower than 3.0 
--Please use script in python3 if you are running python version 3.0.

--The script when ran will delete all folders and .txt files from previous run,
please make sure you save the unzipped folders/files and output files before analyzing a new system dump.
