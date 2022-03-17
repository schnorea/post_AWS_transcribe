import json
from sys import argv
from pprint import pprint
from copy import deepcopy 
import datetime
import re


class Transcription(object):
    def __init__(self, filename):
        self.debug = False
        self.transcription_object = None
        self.processed = None

        self.jobName = None
        self.accountId = None
        self.processed_time = None

        self._load_json_file(filename)

    def _load_json_file(self, filename):
        try:
            with open(filename, "r") as ifh:
                mystery_json = json.load(ifh)
        except IOError:
            print(f"ERROR: File {filename} is not accessible")
            exit(1)
        # Figure out if this is an orginal transcription object or
        # a process speaker_label, content, type, start_time, end_time
        # object
        if self._is_transcription_object(mystery_json):
            # process the thing
            pass
            self.transcription_object = mystery_json
            self._get_meta_info(mystery_json)
            self._weave_in_words()
        elif self._is_processed_object(mystery_json):
            # don't process
            pass
            self.processed = mystery_json
            self._get_meta_info(mystery_json)
        else:
            print(f"ERROR: File {filename} is not an original AWS Transcribe or processed json file")
            exit(1)
        
    def _get_meta_info(self, json_obj):
        self.jobName = json_obj['jobName']
        self.accountId = json_obj['accountId']
        if 'processed_time' in json_obj:
            self.processed_time = json_obj['processed_time']
        

    def save_labeled_words_json(self, filename):
        result = self.processed
        if self.processed is not None:
            with open(filename, "w") as ofh:
                json.dump(result, ofh, indent=4, sort_keys=True)


    def _is_transcription_object(self, json_obj):
        # "jobName":"LineageSecondHalfofSecondDay","accountId":"832014947281","results":{}
        if 'jobName' in json_obj and \
        'accountId' in json_obj and \
        'results' in json_obj and \
        not 'processed_time' in json_obj and \
        not 'type' in json_obj:
            return True
        return False

    def _is_processed_object(self, json_obj):
        # "jobName":"LineageSecondHalfofSecondDay","accountId":"832014947281","processed_time":"167863178518", results":[]
        if 'jobName' in json_obj and \
        'accountId' in json_obj and \
        'results' in json_obj and \
        'processed_time' in json_obj and \
        'type' in json_obj and \
        json_obj['type'] == 'words':
            return True
        return False

    def _parse_debug_line(self, line):
        # Label files are of the format 
        #          "start_time <tab> end_time <tab> label_string <newline>"
        # Debug label_strings are of the format
        #          "speaker_label + f" >{index}> " + content_string"
        line_pattern = r'^\s*([0-9\.]+)\s([0-9\.]+)\s(.+)'
        debug_str_pattern = r'([^>]+)>([0-9]+)>\s+(.+)'
        line_match = re.search(line_pattern, line)
        if line_match is not None:
            start_time = line_match.group(1)
            end_time = line_match.group(2)
            debug_str = line_match.group(3)
        else:
            return -1, line
        debug_match = re.search(debug_str_pattern, debug_str)
        if debug_match is not None:
            speaker_label = debug_match.group(1).strip()
            content_index = int(debug_match.group(2))
            content = debug_match.group(3).strip()
            # Check if content_index makes sense
            if content_index > len(self.processed['results']) or content_index < 0:
                return -3, debug_str
            return content_index, start_time, end_time, speaker_label, content
        return -2, debug_str

    def _look_match_modify(self, line_parts):
        content_index, start_time, end_time, speaker_label, content = line_parts
        word_obj = self.processed['results'][content_index]
        w_start_time = word_obj['start_time']
        w_end_time = word_obj['end_time']
        w_speaker_label = word_obj['speaker_label']
        w_content = word_obj['content']

        # See if start and end times match (might want to add some margin here later)
        start_match = float(w_start_time) == float(start_time)
        end_match = float(w_end_time) == float(end_time)
        if not start_match:
            print(f"Start times don't match for index {content_index} word {w_start_time} label {start_time}")
        if not end_match:
            print(f"End times don't match for index {content_index} word {w_end_time} label {end_time}")

        speaker_match = w_speaker_label == speaker_label
        if not speaker_match:
            print(f"Speaker_labels don't match for index {content_index} word {w_speaker_label} label {speaker_label}")

        content_math = w_content == content
        if not content_math:
            print(f"Content doesn't match for index {content_index} word {w_content} label {content}")



    def load_edited_debug_label_file(self, debug_label_filename):
        # Check to see if it is a label file and that it matches the loaded processed
        # object.
        try:
            with open(debug_label_filename, "r") as ifh:
                lines = ifh.readlines()
        except IOError:
            print(f"ERROR: File {filename} is not accessible in 'load_edited_debug_label_file'")
            exit(1)
        all_line_parts = []
        for line_number, line in enumerate(lines):
            line_parts = self._parse_debug_line(line)
            if len(line_parts) == 2 and line_parts[0] == -1:
                # Bad line
                print(f"ERROR: In file '{debug_label_filename}' the line format didn't match the format below at line {line_number + 1}")
                print(f"Expected debug line format is 'start_time as float' 'tab character' 'end_time as float' 'tab character' 'debug_str'")
                print(f"Example: '234.21\\t309.1\\tspr_1 >14> soap'")
                print(f"What was found (pipes added to denote start and end of string) |{line_parts[1]}|")
                print(f"Please correct and resubmit")
                exit(1)
            elif len(line_parts) == 2 and line_parts[0] == -2:
                # Bad debug_str
                print(f"ERROR: In file '{debug_label_filename}' the line format was fine but the debug_str format didn't match on line {line_number + 1}")
                print(f"The debug_str should have this format 'speecher_label' '>' 'index_number as int' '>' 'content string'")
                print(f"Example: 'Paul Johns >92> Towel'")
                print(f"What was found (pipes added to denote start and end of string) |{line_parts[1]}|")
                print(f"Please correct and resubmit")
                exit(2)
            elif len(line_parts) == 2 and line_parts[0] == -3:
                # Bad content_index
                print(f"ERROR: In file '{debug_label_filename}' the line format was fine but in the debug_str 'index_number' was out of range on line {line_number + 1}")
                print(f"The debug_str should have this format 'speecher_label' '>' 'index_number as int' '>' 'content string'")
                print(f"index_number should be greater than zero and less than or equal to the length of the transcription.")
                print(f"You might want to check if the label file and the word JSON file are from the same transcription.")
                print(f"What was found (pipes added to denote start and end of string) |{line_parts[1]}|")
                print(f"Please correct and resubmit")
                exit(3)
            elif len(line_parts) == 5:
                # Good line match or modify existing words
                all_line_parts.append(line_parts)
        # Check if all_line_parts length matches what is in self.processed
        if len(all_line_parts) != len(self.processed['results']):
            # Labels and words lengths don't match
            print(f"ERROR: The label file '{debug_label_filename}'s number of lines don't match what is found in the JSON word file loaded or")
            print(f"the JSON transcription file loaded length. Label length {len(all_line_parts)} Word length {len(self.processed['results'])}")
            print(f"You might want to check if the label file and the word JSON file are from the same transcription.")
            print(f"Please correct and resubmit")
            exit(4)
        else:
            for line_parts in all_line_parts:
                self._look_match_modify(line_parts)

    def _has_speaker_ids(self):
        results = self.transcription_object['results']
        return ('speaker_labels' in results)

    def get_segments(self):
        return self.transcription_object['results']['speaker_labels']['segments']

    def get_speakers(self):
        return self.transcription_object['results']['speaker_labels']['speakers']

    def get_items(self):
        # Items gives confidence values for words and punctuation
        return self.transcription_object['results']['items']  # Items gives confidence values for words and punctuation

    def speaker_id_segments(self):
        # {'start_time': '5251.88', 'speaker_label': 'spk_1', 'end_time': '5252.22'}
        result = []
        segments = self.transcription_object['results']['speaker_labels']['segments']
        for s in segments:
            items = s['items']
            for i in items:
                result.append(i)
        return result

    def words_and_punctuations(self):
        result = []
        items_group = self.transcription_object['results']['items']  # Items gives confidence values for words and punctuation
        for item in items_group:
            result.append(item)
        return result

    def words_and_punctuations_plus_timing(self):
        result = []
        items_group = deepcopy(self.transcription_object['results']['items'])  # Items gives confidence values for words and punctuation
        for item in items_group:
            if not "end_time" in item:
                item['end_time'] = "NA"
            if not "start_time" in item:
                item['start_time'] = "NA"
            result.append(item)
        return result

    def make_pp_lookup(self, wppp_timing):
        result = {}
        for i,v in enumerate(wppp_timing):
            start_time = v['start_time']
            if 'NA' in start_time:
                continue
            if start_time in result:
                # There is overlap in timing 
                print('WARNING: There is overlap in the pp_lookup', start_time, i, result[start_time])
                print('This may cause and issue')
            result[start_time] = i
            p_v = v
        return result
    
    def _weave_in_words(self):
        """ Takes the speaker id, items sections and weaves these together to form a transcription
        object. 
        """
        if not self._has_speaker_ids():
            print("ERROR: This transcribe json file doesn't have speaker id labels."
                  "resubmitting to AWS Transcribe and enable speaker id")
            exit(1)

        # The speaker id segments will not include time stamped segments for punctuation 
        # and they don't include the word/content/otterance information
        spk_id_segs = deepcopy(self.speaker_id_segments())
        # Words_plus_punctuations_
        wppp_timing = self.words_and_punctuations_plus_timing()
        wppp_lookup = self.make_pp_lookup(wppp_timing)

        if self.debug:
            print("spk_id_segs", len(spk_id_segs))
            print("wppp_timing",len(wppp_timing))
            print("wppp_lookup", len(wppp_lookup))
            print("expected punctation diff", len(wppp_timing) - len(wppp_lookup) )
        wpl = {}

        result = []
        pun_count = 0
        for si, sis in enumerate(spk_id_segs):
            # The speaker labels segment will not include segments for punctuation 
            # and they don't include the word/content/otterance information
            start_time = sis['start_time']
            speaker_id = sis['speaker_label']
            end_time   = sis['end_time']

            # given the start_time of a word/content/otterance look up its index
            # in the word/content/otterance list
            wp_index = wppp_lookup[start_time]
            wp = wppp_timing[wp_index]
            wp_start_time = wp['start_time']
            wp_type_name = wp['type']
            wp_content = wp['alternatives'][0]['content']

            # Add the word/content/otterance to the speaker labls segment
            sis['content'] = wp_content
            sis['type'] = wp_type_name
            # append to result
            result.append(sis)

            # see if the next word/content/otterance is punctuation
            if wp_index + 1 < len(wppp_timing):
                wp_p_1 = wppp_timing[wp_index + 1]
                wp_p_1_type_name = wp_p_1['type']
                if "punc" in wp_p_1_type_name:
                    # It is punctuation so assume that it was the result of the same 
                    # speaker and create a new speaker label entry
                    sip = {}
                    sip['speaker_label'] = sis['speaker_label']
                    sip['content'] = wp_p_1['alternatives'][0]['content']
                    sip['type'] = wp_p_1_type_name
                    # wp_p_1['start_time'] and wp_p_1['end_time'] are currently set to NA
                    # above. This is becuase the timing for punctuation is not taken into account
                    # in the data speaker labeled segments and there is often no time
                    # (segment[n] end_time == segment[n+1] start_time) to insert
                    # the punctation. To fix this some later adjustments is required
                    # Both of these are NA for now
                    sip['start_time'] = wp_p_1['start_time']
                    sip['end_time'] = wp_p_1['end_time']
                    pun_count += 1
                    result.append(sip)
        # Fix start and end timing around punctuation
        for i, sip in enumerate(result):
            if 'punc' in sip['type']:
                # Look before and after
                if i - 1 >= 0 and i + 1 < len(result):
                    prev_end_time = result[i-1]['end_time']
                    next_start_time = result[i+1]['start_time']
                    if prev_end_time == next_start_time:
                        # If these are equal there is no gap in timing to give the punctuation.
                        # To fix this make a small gap
                        new_next_start_time = next_start_time + '001'
                        # push next word back a bit
                        result[i+1]['start_time'] = new_next_start_time
                        # Slide the punctation in the gap
                        sip['start_time'] = prev_end_time
                        sip['end_time'] = new_next_start_time
                    else:
                        # There is a gap.  Exploit it
                        sip['start_time'] = prev_end_time
                        sip['end_time'] = prev_end_time  + '001'

                elif not(i - 1 >= 0) and i + 1 <= len(result):
                    next_start_time = result[i+1]['start_time']
                    # Punctuation at the very begining of the list?
                    new_next_start_time = next_start_time + '001'
                    # push next word back a bit
                    result[i+1]['start_time'] = new_next_start_time
                    # Slide the punctation in the gap
                    sip['start_time'] = next_start_time
                    sip['end_time'] = new_next_start_time
                elif i - 1 >= 0 and not(i + 1 < len(result)):
                    prev_end_time = result[i-1]['end_time']
                    # Punctuation at the very end of the list
                    new_end_time = prev_end_time + '001'
                    # Slide the punctation in the gap
                    sip['start_time'] = prev_end_time
                    sip['end_time'] = new_end_time
        if self.debug:
            print("weave_in_words punctuation count found",pun_count)

        results = {}
        results['jobName'] = self.jobName
        results['accountId'] = self.accountId
        if self.processed_time is None:
            results['processed_time'] = str(datetime.datetime.now())
        else:
            results['processed_time'] = self.processed_time
        results['type'] = "words"
        results['results'] = result

        self.processed = results
    
    def get_labeled_words(self):
        return self.processed

    def get_transcription_json(self):
        result = []
        # Get speaker label, content (including punctuation)

        sicp = self.processed['results']

        current_speaker = sicp[0]['speaker_label']
        current_start_time = sicp[0]['start_time']
        current_end_time = sicp[0]['end_time']
        current_content = ""

        for event in sicp:
            if current_speaker != event['speaker_label']:
                # Change speaker
                # Finish and store last speaker
                otterances = {}
                otterances['speaker_label'] = current_speaker
                otterances['start_time'] = current_start_time
                otterances['end_time'] = current_end_time
                otterances['content'] = current_content
                result.append(otterances)
                # Start next otterance
                current_speaker = event['speaker_label']
                current_start_time = event['start_time']
                current_end_time = event['end_time']
                current_content = event['content']
            else:
                # Accumulate content
                current_end_time = event['end_time']
                if 'punctuation' in event['type']:
                    current_content += event['content']
                else:
                    current_content = current_content + " " + event['content']
        # Finish and store last speaker
        otterances = {}
        otterances['speaker_label'] = current_speaker
        otterances['start_time'] = current_start_time
        otterances['end_time'] = current_end_time
        otterances['content'] = current_content
        result.append(otterances)

        results = {}
        results['jobName'] = self.jobName
        results['accountId'] = self.accountId
        results['processed_time'] = self.processed_time
        results['type'] = "transcription"
        results['results'] = result

        return results

    def save_transcription_json(self, filename):
        result = self.get_transcription_json()
        if self.processed is not None:
            with open(filename, "w") as ofh:
                json.dump(result, ofh, indent=4, sort_keys=True)

    def make_audacity_label_correction_file(self, base_filename):
        """ Makes to label files for audacity:
        1) Shows speaker as related to sound
        2) Shows speaker and Content as related to sound
        """
        sicp = self.processed['results']

        speaker_content_labels = []
        for i, otterance in enumerate(sicp):
            speaker = otterance['speaker_label']
            start_time = otterance['start_time']
            end_time = otterance['end_time']
            content = otterance['content']
            speaker_content_labels.append([start_time, end_time, speaker + f" >{i}> " + content])

        # Output to file
        with open(f"{base_filename}_speaker_debug_labels.txt", "w") as ofh:
            for start, end, label in speaker_content_labels:
                ofh.write(f"{start}\t{end}\t{label}\n")


    def make_audacity_label_files(self, base_filename):
        """ Makes to label files for audacity:
        1) Shows speaker as related to sound
        2) Shows speaker and Content as related to sound
        """
        wiw = self.get_transcription_json()['results']
    
        speaker_labels = []
        content_labels = []
        for i, otterance in enumerate(wiw):
            speaker = otterance['speaker_label']
            start_time = otterance['start_time']
            end_time = otterance['end_time']
            content = otterance['content']
            speaker_labels.append([start_time, end_time, speaker])
            content_labels.append([start_time, end_time, speaker + ">>>" + content])

        # Output to file
        with open(f"{base_filename}_speaker_labels.txt", "w") as ofh:
            for start, end, label in speaker_labels:
                ofh.write(f"{start}\t{end}\t{label}\n")

        with open(f"{base_filename}_content_labels.txt", "w") as ofh:
            for start, end, label in content_labels:
                ofh.write(f"{start}\t{end}\t{label}\n")


if __name__ == "__main__":
    # Examples of usage
    # Call on file path for either AWS Transcribe JSON output file or 
    # P
    t = Transcription(argv[1])
 
    # Create label files for Audacity. Two files created one with just speaker labels
    # The other with speaker labels and full content
    t.make_audacity_label_files(argv[2])

    # Create label file with speaker label, word index and word content (for later correcting miss labeled  speaker)
    t.make_audacity_label_correction_file(argv[2])

    # Save intermediate each word and punctuation with speaker_label, times, and type
    t.save_labeled_words_json(f"{argv[2]}_processed.json")
    # Save Transcription (spoken otterances with speak_labels and start_time and end time)
    t.save_transcription_json(f"{argv[2]}_transcription.json")

