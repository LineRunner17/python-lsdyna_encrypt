from encrypt_lsdyna import LS_Dyna_Encryptor

lde = LS_Dyna_Encryptor(inputfile = 'test.key', expiry_date = '05/01/2024')
# uncomment to encrypt only specific keywords
# lde.keywords_to_encrypt = ['*DEFINE_CURVE']
lde.encrypt_file()
