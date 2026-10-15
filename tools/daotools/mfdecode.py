"""Decode audio files to PCM with Windows Media Foundation (Windows only).

Unreal's Windows media player (WmfMedia) plays the voice-over through the
system mixer, and in that mode it only plays uncompressed PCM. The VO is MP3,
and the standard library has no MP3 decoder, so this asks Windows to decode
it with its own MP3 decoder, through Media Foundation's source reader and
ctypes. Nothing is installed or changed on the system.
"""

from __future__ import annotations

import ctypes
import struct
import sys
import uuid
from ctypes import byref, c_uint32, c_uint64, c_void_p, c_wchar_p

MF_VERSION = 0x00020070
MF_SOURCE_READER_FIRST_AUDIO_STREAM = 0xFFFFFFFD
MF_SOURCE_READERF_ENDOFSTREAM = 0x2

MF_MT_MAJOR_TYPE = "48eba18e-f8c9-4687-bf11-0a74c9f96a8f"
MF_MT_SUBTYPE = "f7e34c9a-42e8-4714-b74b-cb29d72c35e5"
MF_MT_AUDIO_NUM_CHANNELS = "37e48bf5-645e-4c5b-89de-ada9e29b696a"
MF_MT_AUDIO_SAMPLES_PER_SECOND = "5faeeae7-0290-4c31-9e8a-c534f68d9dba"
MF_MT_AUDIO_BITS_PER_SAMPLE = "f2deb57f-40fa-4764-aa33-ed4f2d1ff669"
MFMediaType_Audio = "73647561-0000-0010-8000-00aa00389b71"
MFAudioFormat_PCM = "00000001-0000-0010-8000-00aa00389b71"

# COM vtable slots used below (IUnknown is 0-2; IMFAttributes 3-32).
_RELEASE = 2
_GET_UINT32, _SET_UINT32, _SET_GUID = 7, 21, 24
_READER_GET_CURRENT_TYPE, _READER_SET_CURRENT_TYPE, _READER_READ_SAMPLE = 6, 7, 9
_SAMPLE_TO_CONTIGUOUS = 41
_BUFFER_LOCK, _BUFFER_UNLOCK = 3, 4


class DecodeError(Exception):
    pass


class _GUID(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_ubyte * 16)]

    @classmethod
    def of(cls, text: str) -> "_GUID":
        g = cls()
        ctypes.memmove(g.bytes, uuid.UUID(text).bytes_le, 16)
        return g


def _call(obj: c_void_p, slot: int, *args, argtypes=()):
    vtable = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(c_void_p))).contents
    fn = ctypes.WINFUNCTYPE(ctypes.HRESULT, c_void_p, *argtypes)(vtable[slot])
    return fn(obj, *args)


def _release(obj: c_void_p) -> None:
    if obj:
        vtable = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(c_void_p))).contents
        ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)(vtable[_RELEASE])(obj)


def available() -> bool:
    return sys.platform == "win32"


def decode(path: str) -> tuple[int, int, int, bytes]:
    """(sample rate, channels, bits per sample, PCM bytes) for an audio file."""
    if not available():
        raise DecodeError("decoding to PCM needs Windows Media Foundation (Windows only)")
    mfplat, mfreadwrite = ctypes.WinDLL("mfplat"), ctypes.WinDLL("mfreadwrite")
    ole32 = ctypes.WinDLL("ole32")
    mfplat.MFCreateMediaType.restype = ctypes.HRESULT
    mfreadwrite.MFCreateSourceReaderFromURL.restype = ctypes.HRESULT
    ole32.CoInitializeEx(None, 0)
    if mfplat.MFStartup(MF_VERSION, 0) < 0:
        raise DecodeError("MFStartup failed")
    reader, wanted, actual = c_void_p(), c_void_p(), c_void_p()
    try:
        try:
            mfreadwrite.MFCreateSourceReaderFromURL(c_wchar_p(str(path)), None, byref(reader))
            mfplat.MFCreateMediaType(byref(wanted))
            _call(wanted, _SET_GUID, byref(_GUID.of(MF_MT_MAJOR_TYPE)), byref(_GUID.of(MFMediaType_Audio)),
                  argtypes=(c_void_p, c_void_p))
            _call(wanted, _SET_GUID, byref(_GUID.of(MF_MT_SUBTYPE)), byref(_GUID.of(MFAudioFormat_PCM)),
                  argtypes=(c_void_p, c_void_p))
            _call(wanted, _SET_UINT32, byref(_GUID.of(MF_MT_AUDIO_BITS_PER_SAMPLE)), 16,
                  argtypes=(c_void_p, c_uint32))
            _call(reader, _READER_SET_CURRENT_TYPE, MF_SOURCE_READER_FIRST_AUDIO_STREAM, None, wanted,
                  argtypes=(c_uint32, c_void_p, c_void_p))
            _call(reader, _READER_GET_CURRENT_TYPE, MF_SOURCE_READER_FIRST_AUDIO_STREAM, byref(actual),
                  argtypes=(c_uint32, c_void_p))
        except OSError as e:
            raise DecodeError(f"{path}: Media Foundation could not open it ({e})") from None
        values = []
        for key in (MF_MT_AUDIO_SAMPLES_PER_SECOND, MF_MT_AUDIO_NUM_CHANNELS, MF_MT_AUDIO_BITS_PER_SAMPLE):
            v = c_uint32()
            _call(actual, _GET_UINT32, byref(_GUID.of(key)), byref(v), argtypes=(c_void_p, c_void_p))
            values.append(v.value)
        rate, channels, bits = values

        pcm = bytearray()
        while True:
            index, flags, stamp, sample = c_uint32(), c_uint32(), c_uint64(), c_void_p()
            _call(reader, _READER_READ_SAMPLE, MF_SOURCE_READER_FIRST_AUDIO_STREAM, 0, byref(index),
                  byref(flags), byref(stamp), byref(sample),
                  argtypes=(c_uint32, c_uint32, c_void_p, c_void_p, c_void_p, c_void_p))
            if sample:
                buffer = c_void_p()
                _call(sample, _SAMPLE_TO_CONTIGUOUS, byref(buffer), argtypes=(c_void_p,))
                data, max_len, cur_len = c_void_p(), c_uint32(), c_uint32()
                _call(buffer, _BUFFER_LOCK, byref(data), byref(max_len), byref(cur_len),
                      argtypes=(c_void_p, c_void_p, c_void_p))
                pcm += ctypes.string_at(data, cur_len.value)
                _call(buffer, _BUFFER_UNLOCK)
                _release(buffer)
                _release(sample)
            if flags.value & MF_SOURCE_READERF_ENDOFSTREAM:
                break
        return rate, channels, bits, bytes(pcm)
    finally:
        for obj in (actual, wanted, reader):
            _release(obj)
        mfplat.MFShutdown()


def pcm_wav(rate: int, channels: int, bits: int, pcm: bytes) -> bytes:
    """A plain PCM .wav file."""
    align = channels * bits // 8
    fmt = struct.pack("<HHIIHH", 1, channels, rate, rate * align, align, bits)
    body = (b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
            + b"data" + struct.pack("<I", len(pcm)) + pcm + (b"\0" if len(pcm) % 2 else b""))
    return b"RIFF" + struct.pack("<I", len(body)) + body
