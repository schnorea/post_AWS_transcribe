# AWS Transcribe - How To

General note: To make this accessible to more people the AWS instructions will use the web based "console" as this is easier and doesn't require installing anything on your machine.  Those that use AWS SDK and AWS CLI will probably know how to translate these instructions to there way of interacting with AWS.

## Dependancies 

### AWS Account

These instructions assume that you have a AWS account. If you don't have one instructions for getting one can be found at the link below. 

#### WARNING YOU WILL NEED A CREDIT CARD

https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/

### Need an S3 Bucket
Here is a link to a video of creating an S3 Bucket

https://youtu.be/i4YFFWcyeFM?t=47

### Need an MP3 of the speech that you want to convert to text
Here is a link to youtube search for recording audio interviews

https://www.youtube.com/results?search_query=Recording+an+interview+to+mp3

## How-To
### Step 1 Upload MP3 to the S3 Bucket created above

Here is a video that describes the upload process

https://youtu.be/ftMHNxvV4Ps?t=53

### Step 2 Create a Transcript Job

Go to AWS Transcribe

<img src="/assets/03_Go_to_Transcribe.png?raw=true" alt="drawing" width="400"/>

### Step 3 Select From Right Menu

Select this *Create Transcript* right menu

<img src="/assets/04_Press_Create_Transcipt.png?raw=true" alt="drawing" width="400"/>

### Step 4 Select From Left Menu

Select *Transcription Jobs* from left menu

<img src="/assets/05_Select_Transcript_Job.png?raw=true" alt="drawing" width="400"/>

### Step 5 Create a Job

Select the *Create Job* on the upper right side above the table.

<img src="/assets/06_Create_Job.png?raw=true" alt="drawing" width="400"/>

### Step 6 Give the Job and Point to the MP3

In the form give the job a name and down below browse to the MP3 you uploaded above

<img src="/assets/07_Name_and_Browse.png?raw=true" alt="drawing" width="500"/>

### Step 7 Select to Output the Results to Your S3 Bucket

In the form select *Customer Selected S3 Bucket* and browse to the bucket where the MP3 is to indicate where to put the resulting JSON file when the transcription job is completed.

Make sure to then press the next button at the bottom of the form.

<img src="/assets/08_Output_to_previous_bucket.png?raw=true" alt="drawing" width="500"/>

### Step 8 

In this form select *Audio Identification* and choose *Speaker Identifcation*.  Then press the *Create Job* button at the bottom of the form.

<img src="/assets/09_Setup_Speaker_ID_Finalize_Job.png?raw=true" alt="drawing" width="500"/>

### Step 9

You will be taken back to the Transcribe Jobs table and you should see your project being processed.

### Step 10 

When the job is completed browse back to S3 and to the bucket you selected to hold the resulting JSON file.

### Step 11

Find and select the JSON file created.  It should be named the same as the job create and ends in ```.json```.

### Step 12

With the file selected go to the top of the page and download the file to you local computer.  

You are now ready to use the process_trans.py script.

