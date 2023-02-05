"""Example of CKKS addition."""
from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
import cmath
import os
class fhe:
    def __init__(self):
        print("Generated Keys for this election. Please keep Keys in a safe location.")
        self.generate_key()

    def generate_key(self):
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
        
        #put else where
        self.secret_key = key_generator.secret_key

        self.relin_key = key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, self.public_key, self.secret_key)
        self.decryptor = CKKSDecryptor(self.params, self.secret_key)
        self.evaluator = CKKSEvaluator(self.params)
    
    def fhe_encrypt(self, plain_text, election_area, election_party, election):
        plain_text_encode = self.encoder.encode(plain_text, self.scaling_factor)
        ciph1 = self.encryptor.encrypt(plain_text_encode)
        print(os.getcwd())
        with open(f"./encrypted_votes/{election_area}_{election_party}_{election}_c0.txt", "w") as f:
            f.write(str(ciph1.c0.coeffs))
            f.close()
        with open(f"./encrypted_votes/{election_area}_{election_party}_{election}_c1.txt", "w") as f:
            f.write(str(ciph1.c1.coeffs))
            f.close()
        return ciph1

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
    