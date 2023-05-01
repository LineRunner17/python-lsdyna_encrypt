# python-lsdyna_encrypt
Python script to encrypt LS-Dyna input files

## Background

This Python script is able to partially encrypt LS-Dyna input/key files based on the encryption algorithm provided by LSTC/ANSYS. 'gpg' is used for the encryption process.
For more information on the general gpg encryption process, please refer to the GnuPG project at https://gnupg.org/. For more information on the encryption in the LS-Dyna enviroment please refer to these instructions. (https://ftp.lstc.com/anonymous/outgoing/support/FAQ/Instructions_encryption)

Most often, encryption is used to encrypt material cards and the associated know-how. Since it is quite expensive to create material cards, a common way is to exchange material cards only in encrypted form. For the widely used **\*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE** or **\*MAT_024**, the know-how is based on the corresponding curves. Therefore this script encrypts only **\*DEFINE_CURVE{_TITLE}** and **\*DEFINE_TABLE{_TITLE}** by default.

According to Dynamore Germany, it is in principle also possible to partially encrypt the key files without completely encrypting the keywords. I was also able to test and confirm this myself. This will be added to this script in one of the next versions.

It is also possible to include an expiry date in the encryption. The **\*VENDOR** keyword is used for this purpose. Unfortunately, it is not possible to encrypt a keyword only partially together with an expiry date. That is, if an expiry date is to be used, it is only possible to encrypt whole keywords.

For example:
For a **\*DEFINE_CURVE{_TITLE}** keyword, it would be sufficient to encode only the x-y data of the curve to protect the know-how. Then the following keyword:
```
*DEFINE_CURVE_TITLE
$# title
Example Curve
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
         1         0       1.0       1.0       0.0       0.0
$#                a1                  o1
                 0.0                 0.0
                 1.0                 1.0
```
would look like this:
```
\*DEFINE_CURVE_TITLE
\$# title
Example Curve
\$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
         1         0       1.0       1.0       0.0       0.0
-----BEGIN PGP MESSAGE-----

hQEOAx24cNFeERoiEAQA28d5w5T5nLtw2sAIMceEh0UZZ1ncFPEvKGKWjfLzuiNN
+xx0KQKZIz81UCmB9t9pzU+DNF4/leOv3yXRTJj+n0Zp66EQgqOYCPrfBrvZQlp8
fOgAZ8Eca9xhoisbYky+bQqjjT+PnG7dqzzyF0R1xrqKbKzucYCmRlrgBwmaNugD
/i6mBUgxJ/nqcUHGVK9hMYZWbr0Duk6o/VmWz1gug0/pQ+GTnmUQpswEkOgdMHwP
cQMdLAF9g92EPqol1PJMt4MidI+KFwm8K5lNr/2+SitC8gIH45SQRdfSJq1VAkEf
leS1bu0C7a22N3RQYIBsSQwMAIbsgEeknMR72U8aDRj9ybOfr5KLLa+XwKcI6OBn
YJHbXxuEKOQhrQaWZahLrzT4Z+jm6GBi8z2SG1isIgx+27dfRiDhFsCxrP4xabG6
natJ/dM/KYbRA00kEGh5pK4qFGW1U/USfZt5G037CY/eJVtHSarQKAAPnupOE5/2
oeQXKdmWZT7qPoTywT+BUk0vkxc01u5ympD1R9w+qecfyfOGGgYbFyE61zkO/oMY
HVNtK7fWtImiQpJum2J+sY3KQolVvQ==
=BJyZ
-----END PGP MESSAGE-----
```

But as already mentioned, this method does not allow you to specify an expiration date.

## THE *VENDOR Keyword

The keyword **\*VENDOR** is intended only for an expiration date within an encryption. The usage is as follows:
```
*VENDOR
DATE      05/01/2024
This could be a self-written error message in the VENDOR keyword
*DEFINE_CURVE_TITLE
$# title
Exmaple Curve
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
         1         0       1.0       1.0       0.0       0.0
$#                a1                  o1
                 0.0                 0.0
                 1.0                 1.0
*VENDOR_END
```
This would allow the use of this then encrypted curve until May 1, 2024. Also the error message until the next *Keyword is printed in the message file or d3hsp. Please note that the LS-Dyna uses the server date to check against the expiration date. I.e. if you have an encrypted file, you can still run simulations with this encrypted file if you manually reset the server date to a date before the expiration date.

## Requirements
* Python3.6 and above
* Tested in various LINUX enviroments
* Not in Windows, but should work
## Example Usage
* On the CLI:
```
>>> python3 encrypt_lsdyna.py test.key
```

* As script (See also [test_encrypt_lsdyna.py](examples/test_encrypt_lsdyna.py) for this example.)
Please note that all arguments **must** be keyword arguments.
```python
from encrypt_lsdyna import LS_Dyna_Encryptor

lde = LS_Dyna_Encryptor(inputfile = 'test.key', expiry_date = '05/01/2024')
lde.encrypt_file()
```

If you want to encrypt different keywords than the default ones, you can set them like this. The script will search if the keyword startswith the given *keyword_to_encrypt*. This can have some pitfalls and will need to be explored in more detail at a later date.
```python
from encrypt_lsdyna import LS_Dyna_Encryptor

lde = LS_Dyna_Encryptor(inputfile = 'test.key', expiry_date = '05/01/2024')
lde.keywords_to_encrypt = ['*DEFINE_CURVE']
lde.encrypt_file()
```

## Testing of Encrypted LS-Dyna input

Since it is not possible to decrypt the encrypted key files without the private key, which only LS-Dyna has, the correct encryption can only be verified by an additional simulation run. Up to this point I never had any problems with the code, but please understand that I cannot take any responsibility or warranty.
A simple way to check the encryption is to compare the unencrypted and the encrypted key file. The number of lines of the encrypted file should be greater than the number of lines of the unencrypted key file. The higher the encryption level (1024- or 2048-bit), the greater the difference. With the 1024-bit version, it turned out that the difference is not too big and the encryption really adds only a few lines.

---

## Issues & Ideas

Feel free to submit any issues or ideas for enhancement on the github page: https://github.com/LineRunner17/python-lsdyna_encrypt
If you want to contact me directly: python.dyna@gmail.com

## Future Outlook

I hope this is just the beginning of a Python package for LS-Dyna in particular and other CAE activities in general. I will try to expand the idea in the future.

## License

This code is licensed under **GPL-3.0 license** which basically means you can do whatever you want with it. If you think there will be some issues with the licensing and your project, just reach out to me and I'm sure we will find a solution.
