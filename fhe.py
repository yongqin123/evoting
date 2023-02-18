"""Example of CKKS addition."""
from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
import cmath
import os
from util.polynomial import Polynomial
from util.public_key import PublicKey
from util.secret_key import SecretKey
from util.ciphertext import Ciphertext
#from classes import *


class fhe:
    
    def __init__(self):
        self.load_key()
        #self.generate_key()
    def load_key(self):
        print("Loading keys in progress... ... ...")
        poly_degree = 8
        ciph_modulus = 1 << 600
        big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.params = CKKSParameters(poly_degree=poly_degree,
                                ciph_modulus=ciph_modulus,
                                big_modulus=big_modulus,
                                scaling_factor=self.scaling_factor)
        open_p0 = open('./keys/p0.txt', 'r+')
        read_p0 = open_p0.read().splitlines()
        open_p1 = open('./keys/p1.txt', 'r+')
        read_p1 = open_p1.read().splitlines()
        #open_s1 = open('./keys/s1.txt', 'r+')
        #read_s1 = open_s1.read().splitlines()

        read_p0 = list(map(int,read_p0))
        read_p1 = list(map(int,read_p1))
        #read_s1 = list(map(int,read_s1))

        
        open_p0.close()
        open_p1.close()
        #open_s1.close()
        self.encoder = CKKSEncoder(self.params)
        self.public_key = PublicKey(Polynomial(poly_degree,read_p0),Polynomial(poly_degree,read_p1))
        #self.secret_key = SecretKey(Polynomial(poly_degree,read_s1))
        #self.encryptor = CKKSEncryptor(self.params, self.public_key, self.secret_key)
        self.encryptor = CKKSEncryptor(self.params, self.public_key)
        #self.decryptor = CKKSDecryptor(self.params, self.secret_key)
        self.evaluator = CKKSEvaluator(self.params)

    def uploadSecretKey(self):
        #s2 = open('./keys/fernet_fernet.txt', 'wb')
        
        poly_degree = 8
        ciph_modulus = 1 << 600
        big_modulus = 1 << 1200
        open_s1 = open('./keys/s1.txt', 'r+')
        read_s1 = open_s1.read().splitlines()
        open_s1.close()
        read_s1 = list(map(int,read_s1))
        self.secret_key = SecretKey(Polynomial(poly_degree,read_s1))
        self.decryptor = CKKSDecryptor(self.params, self.secret_key)
        print("secret key uploaded... ...")

    def generate_key(self):
        print("Generating keys in progress... ...")
        poly_degree = 8
        ciph_modulus = 1 << 600
        big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.params = CKKSParameters(poly_degree=poly_degree,
                                ciph_modulus=ciph_modulus,
                                big_modulus=big_modulus,
                                scaling_factor=self.scaling_factor)
        
        key_generator = CKKSKeyGenerator(self.params)
        self.public_key = key_generator.public_key
        print("---Public Key---")
        #print(self.public_key.p0.coeffs)
        #print(self.public_key.p1.coeffs)
        filepk0 = open("./keys/p0.txt", 'w')
        for i in self.public_key.p0.coeffs:
            filepk0.write(str(i)+'\n')
        filepk1 = open("./keys/p1.txt", 'w')
        for i in self.public_key.p1.coeffs:
            filepk1.write(str(i)+'\n')
        #put else where
        self.secret_key = key_generator.secret_key
        print("---Secret key---")
        print(self.secret_key.s.coeffs)
        filesk = open("./keys/s1.txt", 'w')
        for i in self.secret_key.s.coeffs:
            filesk.write(str(i)+'\n')
        filepk0.close()
        filepk1.close()
        filesk.close()
        self.relin_key = key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, self.public_key, self.secret_key)
        self.decryptor = CKKSDecryptor(self.params, self.secret_key)
        self.evaluator = CKKSEvaluator(self.params)
 


    def fhe_encrypt(self, plain_text, election_area, election_party, count):
        plain_text_encode = self.encoder.encode(plain_text, self.scaling_factor)
        ciph1 = self.encryptor.encrypt(plain_text_encode)
        print(os.getcwd())
        
        #count = count + 1
        

        #with open(f"./encrypted_votes/{election_area}_{election_party}_{count}_c0.txt", "w") as f:
        with open(f"./encrypted_votes/{election_area}_{election_party}_{count}_c0.txt", "w") as f:
            for i in ciph1.c0.coeffs:
                f.write(str(i)+'\n')
            f.close()
        with open(f"./encrypted_votes/{election_area}_{election_party}_{count}_c1.txt", "w") as f:
            for i in ciph1.c1.coeffs:
                f.write(str(i)+'\n')
            f.close()
        return ciph1

    def fhe_cipher(self, c0_txt, c1_txt):
        poly_degree = 8
        ciph_modulus = 1 << 600
        big_modulus = 1 << 1200
        with open(f"./encrypted_votes/{c0_txt}", "r+") as f:
            c0 = f.read().splitlines()
            f.close()
        with open(f"./encrypted_votes/{c1_txt}", "r+") as f:
            c1 = f.read().splitlines()
            f.close()
        c0 = list(map(int, c0))
        c1 = list(map(int, c1))
        #print(c0)
        #print(c1)
        cip = Ciphertext(Polynomial(poly_degree, c0), Polynomial(poly_degree, c1), scaling_factor=1 << 30, modulus=ciph_modulus)
        return cip
        
    def fhe_add(self, ciph1, ciph2):
        ciph3 = self.evaluator.add(ciph1, ciph2)
        return ciph3

    def fhe_decrypt(self, ciph):
        decrypted_plain_text_encoded = self.decryptor.decrypt(ciph)
        decrypted_plain_text = self.encoder.decode(decrypted_plain_text_encoded)
        arr = []
        for i in decrypted_plain_text:
            arr.append(round(i.real))
        #print(decoded_prod)
        return arr
    
    
'''

a = fhe()

#print(a.fhe_decrypt(a.fhe_cipher("Sengkang GRC_WAP_3_c0.txt", "Sengkang GRC_WAP_3_c1.txt")))
#print(a.fhe_decrypt(a.fhe_cipher("Sengkang GRC_Sun Party_3_c0.txt", "Sengkang GRC_Sun Party_3_c1.txt")))
#print(a.fhe_decrypt(a.fhe_cipher("Sengkang GRC_Thunder Party_3_c0.txt", "Sengkang GRC_Thunder Party_3_c1.txt")))

boundary = AdminPage()
dict = boundary.controller.filterEncryptedVotesByDistrict(a)
#print(dict)
'''
