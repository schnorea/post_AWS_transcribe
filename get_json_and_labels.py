from process_trans import Transcription
from sys import argv

if __name__ == "__main__":
    # Examples of usage
    # Call on file path for either AWS Transcribe JSON output file or
    # processed labeled words JSON file
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