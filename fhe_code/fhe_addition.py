"""Example of CKKS addition."""

from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
import cmath

def main():

    poly_degree = 8
    ciph_modulus = 1 << 600
    big_modulus = 1 << 1200
    scaling_factor = 1 << 30
    params = CKKSParameters(poly_degree=poly_degree,
                            ciph_modulus=ciph_modulus,
                            big_modulus=big_modulus,
                            scaling_factor=scaling_factor)
    key_generator = CKKSKeyGenerator(params)
    public_key = key_generator.public_key
    secret_key = key_generator.secret_key
    relin_key = key_generator.relin_key
    encoder = CKKSEncoder(params)
    encryptor = CKKSEncryptor(params, public_key, secret_key)
    decryptor = CKKSDecryptor(params, secret_key)
    evaluator = CKKSEvaluator(params)

    message1 = [1000, 4000, 3000, 7891]
    
    #message2 = [0.2, 0.11, 0.4 + 0.67j, 0.9 + 0.99j]
    plain1 = encoder.encode(message1, scaling_factor)
    plain2 = encoder.encode([2,2,2,2], scaling_factor)
    ciph1 = encryptor.encrypt(plain1)
    #ciph2 = encryptor.encrypt(plain2)
    ciph_prod = evaluator.add_plain(ciph1, plain2)
    decrypted_prod = decryptor.decrypt(ciph_prod)
    decoded_prod = encoder.decode(decrypted_prod)
    
    arr = []
    for i in decoded_prod:
        arr.append(round(i.real))
    #print(decoded_prod)
    print(arr)
if __name__ == '__main__':
    main()
