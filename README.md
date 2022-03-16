# post_AWS_transcribe
AWS Transcribe does a reasonable job doing speach to text with speaker id but the json output is crazy.

Recording meetings and other conversations via the computer is easy but when you go back to figure out who said what it is painful. AWS Transcribe allows you to take a mp3 file and convert it to text. AWS Transcribe also will offer to detect the speaks and will identify each word with a speaker_label.  The problem is that the JSON file they hand back is a bit of a bear to try and decypher.  

This script takes a AWS Transcribe JSON output file and processes it into a number of useful formats.

## Sane Objects and JSON Files
The script will create two outputs.

### Words, Punctuation, Times and Speakers
```
{
    "accountId": "333333333333",
    "jobName": "BillTedExcel",
    "processed_time": "2022-03-15 20:35:56.777924",
    "type": "words",
    "results": [
        {
            "content": "now",
            "end_time": "3.83",
            "speaker_label": "spk_0",
            "start_time": "3.14",
            "type": "pronunciation"
        },
        {
            "content": "a",
            "end_time": "3.94",
            "speaker_label": "spk_0",
            "start_time": "3.84",
            "type": "pronunciation"
        },
        {
            "content": "motion",
            "end_time": "4.33",
            "speaker_label": "spk_0",
            "start_time": "3.94",
            "type": "pronunciation"
        },
        {
            "content": "picture",
            "end_time": "4.71",
            "speaker_label": "spk_0",
            "start_time": "4.33",
            "type": "pronunciation"
        },
        {
            "content": ",",
            "end_time": "4.71001",
            "speaker_label": "spk_0",
            "start_time": "4.71",
            "type": "punctuation"
        }
    ]
}
```

### Transcription with Speaker, Times, and Content
```
{
    "accountId": "333333333333",
    "jobName": "BillTedExcel",
    "processed_time": null,
    "results": [
        {
            "content": " now a motion picture, so grand and so magnificent And so vast. It spans 7000 years. no",
            "end_time": "11.67",
            "speaker_label": "spk_0",
            "start_time": "3.14"
        },
        {
            "content": "way.",
            "end_time": "12.6001",
            "speaker_label": "spk_1",
            "start_time": "11.68"
        },
        {
            "content": "Yes way. But it starts with Bill. Bill? S. Preston who was joan of Arc and",
            "end_time": "18.53",
            "speaker_label": "spk_0",
            "start_time": "12.61"
        }
    ]
}
```

## Audacity Labels
The OSS software Audacity has the capabiltiy to add a label track where time intervals that sink with the audio track can be imported.  The imported label track is usefull for visualization and selecting audio segments.

Three label formats can be output.

### Speaker
```
3.14	11.67	spk_0
11.68	12.6001	spk_1
12.61	18.53	spk_0
18.54	23.03001	spk_1
23.04	24.67001	spk_0
24.68	27.48	spk_1
27.48	33.73	spk_0
33.73	47.62001	spk_1
49.39	53.09	spk_0
53.1	53.99	spk_1
55.02	55.93001	spk_0
56.07	58.39	spk_1
59.1	79.76001	spk_0
80.54	81.26001	spk_1
81.26001	91.66001	spk_0
92.54	102.63	spk_1
105.45	109.65	spk_0
```

### Speaker Content
```
3.14	11.67	spk_0>>> now a motion picture, so grand and so magnificent And so vast. It spans 7000 years. no
11.68	12.6001	spk_1>>>way.
12.61	18.53	spk_0>>>Yes way. But it starts with Bill. Bill? S. Preston who was joan of Arc and
18.54	23.03001	spk_1>>>Ted Noah's wife were in danger of flunking most heinously tomorrow.
23.04	24.67001	spk_0>>>A force from the future.
24.68	27.48	spk_1>>>Can we go anywhere we want at any time? You can do
27.48	33.73	spk_0>>>anything you want is putting history at their fingertips. Let's reach out and touch someone. Okay, they're traveling through
33.73	47.62001	spk_1>>>time. How's it going? Royal ugly dudes, put them in the iron meet Excellent, execute them booties. What's going on?
49.39	53.09	spk_0>>>And they're making a big impression. Historical
```

### Debug
```
3.14	3.83	spk_0 >0> now
3.84	3.94	spk_0 >1> a
3.94	4.33	spk_0 >2> motion
4.33	4.71	spk_0 >3> picture
4.71	4.71001	spk_0 >4> ,
4.71001	4.94	spk_0 >5> so
4.94	5.47	spk_0 >6> grand
5.48	5.57	spk_0 >7> and
5.58	6.58	spk_0 >8> so
6.58	7.25	spk_0 >9> magnificent
7.81	8.03	spk_0 >10> And
8.03	8.25	spk_0 >11> so
8.25	8.8	spk_0 >12> vast
8.8	8.8001	spk_0 >13> .
9.01	9.18	spk_0 >14> It
9.18	9.7	spk_0 >15> spans
9.7	10.65	spk_0 >16> 7000
10.65	11.2	spk_0 >17> years
11.2	11.2001	spk_0 >18> .
```

## Install and run
Just copy over the process_trans.py file.  It's Python3.  No modules to install.

```
# First argument path to JSON file. Second is file base name for outputs.
$ python process_trans.py example_input/BillTedExcel.json BillTedOuput
```
 
## Speaker Label Errors
The audio file that was used for the example was a bit extreme in that it had music and cut scene dialog all over the place. The result is that the speaker labeling isn't that good.  Even in more controled environments if there are speakers that are talking over each other there will be label errors.  The Word JSON object allows these error to be corrected more easily.  In the future a more automated way of making corrrection to this JSON file will be added.

The script can consume this file as well (same syntax as above) and then be used to create the transcription and Audacity Label files.

Enjoy!
