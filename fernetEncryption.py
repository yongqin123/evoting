from cryptography.fernet import Fernet

def write_key():
    key = Fernet.generate_key() # Generates the key
    with open("fhe_fernet.key", "wb") as key_file: # Opens the file the key is to be written to
        key_file.write(key) # Writes the key

def load_key():
    return open("fhe_fernet.key", "rb").read() #Opens the file, reads and returns the key stored in the file

#digit1 = "0".encode() # Takes the message as user input and encodes it
write_key() # Writes the key to the key file
key = load_key() # Loads the key and stores it in a variable
f = Fernet(key)
#encrypted_message = f.encrypt(digit1)
#print(encrypted_message)
s1 = open('s1.txt','r')
contents = s1.read().splitlines()
print(contents)
s2 = open('fernet_fhe.txt', 'wb')
for i in contents:
    s2.write(f.encrypt(i.encode()))
    s2.write(b'\n')
s2.close()
'''
s1 = open('s1.txt','r')
contents = s1.read().splitlines()
print(contents)
s1.close()
s2 = open('fernet_fhe.txt', 'wb')
for i in contents:
    s2.write(f.encrypt(i.encode()))
    s2.write(b'\n')
s2.close()



#decrypted_message = f.decrypt(encrypted_message)
#print(int(decrypted_message))


###decrypting###
s3 = open('fernet_encrypt.txt', 'r')
contents = s3.read().splitlines()
print(contents)

for i in contents:
    print(int(f.decrypt(i)))
'''