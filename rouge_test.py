import json
from rouge import Rouge

r1 = 0
p1 = 0
f1 = 0
p2 = 0
p3 = 0
f2 = 0
f3 = 0
r2 = 0
r3 = 0

# Load some sentences
for i in range(648):
    file1 = './email_dataset/finished_files/refs/val/' + str(i) + '.ref' 
    with open(file1) as f:
        data = f.read()
    f.close()

    file2 = './email_dataset/finished_files/output/' + str(i) + '.dec' 
    with open(file2) as f:
      data_1 = f.read()
    f.close()


#hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
    #print(data)
    #print(data_1)

    rouge = Rouge()
    scores = rouge.get_scores(data, data_1)
    for score in scores:
       print(score)
       r1 = r1 + score['rouge-1']['r']
       p1 = p1 + score['rouge-1']['p']
       f1 = f1 + score['rouge-1']['f']
       r2 = r2 + score['rouge-2']['r']
       p2 = p2 + score['rouge-2']['p']
       f2 = f2 + score['rouge-2']['f']
       r3 = r3 + score['rouge-l']['r']
       p3 = p3 + score['rouge-l']['p']
       f3 = f3 + score['rouge-l']['f']
      		
       
 
'''
       for a in score:
           if a == "rouge-1":
               for c,d in b:
                   if c == "r":
                      r1 = r1+d
                   elif c == "f":
                       p1 = p1+d
                   else:
                       f1 = f1+d
           elif a == "rouge-2":
                for c,d in b:
                    if c == "r":
                       r2 = r2+d
                    elif c =="p":
                        p2 = p2+d
                    else:
                        f2 = f2 +d
           else:
                for c,d in b:
                    if state == "r":
                        r3 = r3+d
                    elif state == "p":
                        p3 = p3 + d
                    else:
                        f3 = f3 +d

# or
#scores = rouge.get_scores(hyps, refs, avg=True)
''' 
    print(r1/648)
    print(p1/648)
    print(f1/648)
    print(r2/648)
    print(p2/648) 
    print(f2/648)
    print(r3/648)
    print(p3/648)
    print(f3/648)


