import os

from monkey_island.cc.server_utils.encryption import (
    get_datastore_encryptor,
    initialize_datastore_encryptor,
)

PASSWORD_FILENAME = "mongo_key.bin"

PLAINTEXT = "Hello, Monkey!"
CYPHERTEXT = "vKgvD6SjRyIh1dh2AM/rnTa0NI/vjfwnbZLbMocWtE4e42WJmSUz2ordtbQrH1Fq"


def test_aes_cbc_encryption(data_for_tests_dir):
    initialize_datastore_encryptor(data_for_tests_dir)

    assert get_datastore_encryptor().enc(PLAINTEXT) != PLAINTEXT


def test_aes_cbc_decryption(data_for_tests_dir):
    initialize_datastore_encryptor(data_for_tests_dir)

    assert get_datastore_encryptor().dec(CYPHERTEXT) == PLAINTEXT


def test_aes_cbc_enc_dec(data_for_tests_dir):
    initialize_datastore_encryptor(data_for_tests_dir)

    assert get_datastore_encryptor().dec(get_datastore_encryptor().enc(PLAINTEXT)) == PLAINTEXT


def test_create_new_password_file(tmpdir):
    initialize_datastore_encryptor(tmpdir)

    assert os.path.isfile(os.path.join(tmpdir, PASSWORD_FILENAME))
