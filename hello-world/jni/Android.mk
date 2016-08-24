LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := my_hello_world
LOCAL_SRC_FILES := main.c
include $(BUILD_EXECUTABLE)
