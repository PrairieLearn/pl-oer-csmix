import random, copy

def generate(data):

    data['params']['cport'] = random.randint(49152,65535)
    data['params']['sport'] = random.randint(1000,4000)
    data['params']['client'] = "10.%d.%d.%d" % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254)) 
    data['params']['server'] = "10.%d.%d.%d" % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254)) 

    x = [random.randint(int(1e9), int(2e9)), random.randint(int(3e9), 4294967295)]
    random.shuffle(x)
    data['params']['sn1'] = x[0] 
    data['params']['sn2'] = x[1]

    data['params']['l1'] = random.randint(5, 512)
    data['params']['l2'] = random.randint(5, 512)
    data['params']['ack1'] = data['params']['sn1'] + data['params']['l1']
    data['params']['missed'] = random.choice([True, False])
    if data['params']['missed']:
        data['params']['seq2'] = data['params']['ack1'] + random.randint(5, 512)
        data['correct_answers']['ack'] = data['params']['ack1'] 
    else:
        data['params']['seq2'] = data['params']['ack1'] 
        data['correct_answers']['ack'] = data['params']['ack1'] + data['params']['l2']
