import os, sys, io, zipfile
import urllib.request
import nkf

BASE_DIR = 'train/'
NUC_URL = 'https://nknet.ninjal.ac.jp/nuc/nuc.zip'
NUC_DIR = BASE_DIR + "nuc"
ZIP_DIR = NUC_DIR + '.zip'
SEQUENCE_TXT = BASE_DIR + 'sequence.txt'
INPUT_TXT = BASE_DIR + 'input.txt'
OUTPUT_TXT = BASE_DIR + 'output.txt'

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout = open(SEQUENCE_TXT, "w", encoding='utf-8')

def make_sequence_from_file(fname):
    fname = os.path.join(NUC_DIR, fname)
    if not os.path.exists(fname):
        raise Exception("no %s file." % fname)
    last_line = None
    sequence = []
    input_encoding = 'euc-jp'   # encode自動判定があるとベスト
    with open(fname, "r", encoding=input_encoding) as f:
        try:
            for line in f:
                uline = line
                if uline[0] == '＠':
                    continue
                if uline[0] == 'F' or uline[0] == 'M':
                    if last_line is None:
                        last_line = uline
                        continue
                    else:
                        seq_input = last_line[5:-1]
                        seq_output = uline[5:-1]
                        last_line = uline
                        sequence.append([seq_input, seq_output])
                else:
                    last_line = None
        except:
            sys.stderr.write("skip %s (invalid encoding: %s)\n" % (fname, input_encoding))
            sys.stderr.flush()
            return []
    return sequence

def make_input_file():
    sys.stdout = open(INPUT_TXT, "w", encoding='utf-8')
    # sequence = nkf.nkf('-wXZ0', SEQUENCE_TXT)

    with open(SEQUENCE_TXT, "r", encoding='utf-8') as f:
        txt = 'text'
        for line in f:
            if line.startswith('input: '):
                txt = line.replace('input: ', '')
                txt = txt.rstrip("\n")
                if txt:
                    # TODO 形態素解析
                    print(txt)

    sys.stdout.close()

    return

def make_output_file():
    sys.stdout = open(OUTPUT_TXT, "w", encoding='utf-8')
    # sequence = nkf.nkf('-wXZ0', SEQUENCE_TXT)

    with open(SEQUENCE_TXT, "r", encoding='utf-8') as f:
        for line in f:
            if line.startswith('output: '):
                txt = line.replace('output: ', '')
                txt = txt.rstrip("\n")
                if txt:
                    # TODO 形態素解析
                    print(txt)

    sys.stdout.close()

    return

def download():
    urllib.request.urlretrieve(NUC_URL, ZIP_DIR)

def main():
    if not os.path.exists(ZIP_DIR):
        download()

    with zipfile.ZipFile(ZIP_DIR, "r") as zf:
        zf.extractall(path=os.path.dirname(ZIP_DIR))

    files = os.listdir(NUC_DIR)
    uniq_seq = {}
    for f in files:
        if not ".txt" in f:
            continue
        
        seq = make_sequence_from_file(f)
        for inp, out in seq:
            uniq_seq[inp] = out
    for k, v in uniq_seq.items():
        print("input: %s\noutput: %s" % (k, v))
    sys.stdout.close()

    # 作成したファイルからinputとoutputを分ける
    make_input_file()
    make_output_file()
    return

if __name__ == "__main__":
    main()
    sys.exit(0)
