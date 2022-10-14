#
# Import libraries
from eva import *
from eva.seal import *
from eva.ckks import *

# adding 1 to cypher text
poly = EvaProgram("Polynomial", vec_size=1024)
with poly:
    x = Input("x")
    Output("y", x + 1)
    
poly.set_output_ranges(30)
poly.set_input_scales(30)


# Compile program with CKKS scheme
compiler = CKKSCompiler()
compiled_poly, params, signature = compiler.compile(poly)

# Serializing poly,params,signature
save(poly, 'poly.eva')
save(params, 'poly.evaparams')
save(signature, 'poly.evasignature')

#
# Generate key context
#   public context contains : public key, relin key, galois key
#   secret context contains : secret key
#

public_ctx, secret_ctx = generate_keys(params)

save(public_ctx, 'poly.sealpublic')
save(secret_ctx, 'poly.sealsecret')

#
# Create encryption for x where x = 100,245,31233123,441241242
#
inputs = { "x": [0.0 for i in range(compiled_poly.vec_size)] }
inputs["x"][0] = 100
inputs["x"][1] = 245
inputs["x"][2] = 31233123
inputs["x"][3] = 441241242

encInputs = public_ctx.encrypt(inputs, signature)
save(encInputs, 'poly_inputs.sealvals')

#
# Execute computation
#
poly = load('poly.eva')
public_ctx = load('poly.sealpublic')
encInputs = load('poly_inputs.sealvals')

encOutputs = public_ctx.execute(compiled_poly, encInputs)

save(encOutputs, 'poly_outputs.sealvals')
#
# Decrypt results
#
secret_ctx = load('poly.sealsecret')
encOutputs = load('poly_outputs.sealvals')
outputs = secret_ctx.decrypt(encOutputs, signature)

print("********** Result for y is **********")
for i in range(4):
    print(round(outputs["y"][i]))
