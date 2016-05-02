MY_LOCAL_PATH := $(abspath $(call my-dir))

include $(CLEAR_VARS)
LOCAL_PATH = $(MY_LOCAL_PATH)
LOCAL_MODULE := _cryptography_openssl
LOCAL_SRC_FILES := $(LOCAL_PATH)/../openssl/_cryptography_openssl.c
LOCAL_STATIC_LIBRARIES := python_shared openssl_static opencrypto_static
include $(BUILD_SHARED_LIBRARY)
$(call import-module,python/3.5)
$(call import-module,openssl/1.0.2)

include $(CLEAR_VARS)
LOCAL_PATH = $(MY_LOCAL_PATH)
LOCAL_MODULE := _cryptography_constant_time
LOCAL_SRC_FILES := $(LOCAL_PATH)/../constant_time/_cryptography_constant_time.c
LOCAL_STATIC_LIBRARIES := python_shared
include $(BUILD_SHARED_LIBRARY)
$(call import-module,python/3.5)

include $(CLEAR_VARS)
LOCAL_PATH = $(MY_LOCAL_PATH)
LOCAL_MODULE := _cryptography_padding
LOCAL_SRC_FILES := $(LOCAL_PATH)/../padding/_cryptography_padding.c
LOCAL_STATIC_LIBRARIES := python_shared
include $(BUILD_SHARED_LIBRARY)
$(call import-module,python/3.5)
