# -*- coding: utf-8 -*-
__copyright__ = "Copyright (c) 2014-2017 Agora.io, Inc."

import os
import sys
import time
import hmac
import zlib
import random
import base64
from hashlib import sha256
from collections import OrderedDict
import struct

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def pack_uint16(x):
    return struct.pack('<H', int(x))


def unpack_uint16(buffer):
    data_length = struct.calcsize('H')
    return struct.unpack('<H', buffer[:data_length])[0], buffer[data_length:]


def pack_uint32(x):
    return struct.pack('<I', int(x))


def unpack_uint32(buffer):
    data_length = struct.calcsize('I')
    return struct.unpack('<I', buffer[:data_length])[0], buffer[data_length:]


def pack_int16(x):
    return struct.pack('<h', int(x))


def unpack_int16(buffer):
    data_length = struct.calcsize('h')
    return struct.unpack('<h', buffer[:data_length])[0], buffer[data_length:]


def pack_string(string):
    # if isinstance(string, str):
    #     string = string.encode('utf-8')
    return pack_uint16(len(string)) + string


def unpack_string(buffer):
    data_length, buffer = unpack_uint16(buffer)
    return struct.unpack('<{}s'.format(data_length), buffer[:data_length])[0], buffer[data_length:]


def pack_map_uint32(m):
    return pack_uint16(len(m)) + b''.join([pack_uint16(k) + pack_uint32(v) for k, v in m.items()])


def unpack_map_uint32(buffer):
    data_length, buffer = unpack_uint16(buffer)

    data = {}
    for i in range(data_length):
        k, buffer = unpack_uint16(buffer)
        v, buffer = unpack_uint32(buffer)
        data[k] = v
    return data, buffer


def pack_map_string(m):
    return pack_uint16(len(m)) + b''.join([pack_uint16(k) + pack_string(v) for k, v in m.items()])


def unpack_map_string(buffer):
    data_length, buffer = unpack_uint16(buffer)

    data = {}
    for i in range(data_length):
        k, buffer = unpack_uint16(buffer)
        v, buffer = unpack_string(buffer)
        data[k] = v
    return data, buffer


VERSION_LENGTH = 3


def get_version():
    return '007'


class Service(object):
    def __init__(self, service_type):
        self.__type = service_type
        self.__privileges = {}

    def __pack_type(self):
        return pack_uint16(self.__type)

    def __pack_privileges(self):
        privileges = OrderedDict(
            sorted(iter(self.__privileges.items()), key=lambda x: int(x[0])))
        return pack_map_uint32(privileges)

    def add_privilege(self, privilege, expire):
        self.__privileges[privilege] = expire

    def service_type(self):
        return self.__type

    def pack(self):
        return self.__pack_type() + self.__pack_privileges()

    def unpack(self, buffer):
        self.__privileges, buffer = unpack_map_uint32(buffer)
        return buffer


class ServiceRtc(Service):
    kServiceType = 1

    kPrivilegeJoinChannel = 1
    kPrivilegePublishAudioStream = 2
    kPrivilegePublishVideoStream = 3
    kPrivilegePublishDataStream = 4

    def __init__(self, channel_name='', uid=0):
        super(ServiceRtc, self).__init__(ServiceRtc.kServiceType)
        self.__channel_name = channel_name.encode('utf-8')
        self.__uid = b'' if uid == 0 else str(uid).encode('utf-8')

    def pack(self):
        return super(ServiceRtc, self).pack() + pack_string(self.__channel_name) + pack_string(self.__uid)

    def unpack(self, buffer):
        buffer = super(ServiceRtc, self).unpack(buffer)
        self.__channel_name, buffer = unpack_string(buffer)
        self.__uid, buffer = unpack_string(buffer)
        return buffer


class ServiceRtm(Service):
    kServiceType = 2

    kPrivilegeLogin = 1

    def __init__(self, user_id=''):
        super(ServiceRtm, self).__init__(ServiceRtm.kServiceType)
        self.__user_id = user_id.encode('utf-8')

    def pack(self):
        return super(ServiceRtm, self).pack() + pack_string(self.__user_id)

    def unpack(self, buffer):
        buffer = super(ServiceRtm, self).unpack(buffer)
        self.__user_id, buffer = unpack_string(buffer)
        return buffer


class ServiceFpa(Service):
    kServiceType = 4

    kPrivilegeLogin = 1

    def __init__(self):
        super(ServiceFpa, self).__init__(ServiceFpa.kServiceType)

    def pack(self):
        return super(ServiceFpa, self).pack()

    def unpack(self, buffer):
        buffer = super(ServiceFpa, self).unpack(buffer)
        return buffer


class ServiceChat(Service):
    kServiceType = 5

    kPrivilegeUser = 1
    kPrivilegeApp = 2

    def __init__(self, user_id=''):
        super(ServiceChat, self).__init__(ServiceChat.kServiceType)
        self.__user_id = user_id.encode('utf-8')

    def pack(self):
        return super(ServiceChat, self).pack() + pack_string(self.__user_id)

    def unpack(self, buffer):
        buffer = super(ServiceChat, self).unpack(buffer)
        self.__user_id, buffer = unpack_string(buffer)
        return buffer


class ServiceEducation(Service):
    kServiceType = 7

    kPrivilegeRoomUser = 1
    kPrivilegeUser = 2
    kPrivilegeApp = 3

    def __init__(self, room_uuid='', user_uuid='', role=-1):
        super(ServiceEducation, self).__init__(ServiceEducation.kServiceType)
        self.__room_uuid = room_uuid.encode('utf-8')
        self.__user_uuid = user_uuid.encode('utf-8')
        self.__role = role

    def pack(self):
        return super(ServiceEducation, self).pack() + pack_string(self.__room_uuid) + pack_string(
            self.__user_uuid) + pack_int16(self.__role)

    def unpack(self, buffer):
        buffer = super(ServiceEducation, self).unpack(buffer)
        self.__room_uuid, buffer = unpack_string(buffer)
        self.__user_uuid, buffer = unpack_string(buffer)
        self.__role, buffer = unpack_int16(buffer)
        return buffer


class AccessToken:
    kServices = {
        ServiceRtc.kServiceType: ServiceRtc,
        ServiceRtm.kServiceType: ServiceRtm,
        ServiceFpa.kServiceType: ServiceFpa,
        ServiceChat.kServiceType: ServiceChat,
        ServiceEducation.kServiceType: ServiceEducation
    }

    def __init__(self, app_id='', app_certificate='', issue_ts=0, expire=900):
        random.seed(time.time())

        self.__app_id = app_id
        self.__app_cert = app_certificate

        self.__issue_ts = issue_ts if issue_ts != 0 else int(time.time())
        self.__expire = expire
        self.__salt = random.randint(1, 99999999)

        self.__service = {}

    def __signing(self):
        signing = hmac.new(pack_uint32(self.__issue_ts),
                           self.__app_cert, sha256).digest()
        signing = hmac.new(pack_uint32(self.__salt), signing, sha256).digest()
        return signing

    def __build_check(self):
        def is_uuid(data):
            if len(data) != 32:
                return False
            try:
                bytearray.fromhex(data)
            except:
                return False
            return True

        if not is_uuid(self.__app_id) or not is_uuid(self.__app_cert):
            return False
        if not self.__service:
            return False
        return True

    def add_service(self, service):
        self.__service[service.service_type()] = service

    def build(self):
        if not self.__build_check():
            return ''

        self.__app_id = self.__app_id.encode('utf-8')
        self.__app_cert = self.__app_cert.encode('utf-8')
        signing = self.__signing()
        signing_info = pack_string(self.__app_id) + pack_uint32(self.__issue_ts) + pack_uint32(self.__expire) + \
            pack_uint32(self.__salt) + pack_uint16(len(self.__service))

        for _, service in self.__service.items():
            signing_info += service.pack()

        signature = hmac.new(signing, signing_info, sha256).digest()

        return get_version() + base64.b64encode(zlib.compress(pack_string(signature) + signing_info)).decode('utf-8')

    def from_string(self, origin_token):
        try:
            origin_version = origin_token[:VERSION_LENGTH]
            if origin_version != get_version():
                return False

            buffer = zlib.decompress(
                base64.b64decode(origin_token[VERSION_LENGTH:]))
            signature, buffer = unpack_string(buffer)
            self.__app_id, buffer = unpack_string(buffer)
            self.__issue_ts, buffer = unpack_uint32(buffer)
            self.__expire, buffer = unpack_uint32(buffer)
            self.__salt, buffer = unpack_uint32(buffer)
            service_count, buffer = unpack_uint16(buffer)

            for i in range(service_count):
                service_type, buffer = unpack_uint16(buffer)
                service = AccessToken.kServices[service_type]()
                buffer = service.unpack(buffer)
                self.__service[service_type] = service
        except Exception as e:
            print('Error: {}'.format(repr(e)))
            raise ValueError('Error: parse origin token failed')
        return True


Role_Publisher = 1  # for live broadcaster
Role_Subscriber = 2  # default, for live audience


class RtcTokenBuilder:
    @staticmethod
    def build_token_with_uid(app_id, app_certificate, channel_name, uid, role, token_expire, privilege_expire=0):
        """
        Build the RTC token with uid.
        :param app_id: The App ID issued to you by Agora. Apply for a new App ID from Agora Dashboard if it is missing
            from your kit. See Get an App ID.
        :param app_certificate: Certificate of the application that you registered in the Agora Dashboard.
            See Get an App Certificate.
        :param channel_name: Unique channel name for the AgoraRTC session in the string format.
        :param uid: User ID. A 32-bit unsigned integer with a value ranging from 1 to (2^32-1).
            optionalUid must be unique.
        :param role: Role_Publisher: A broadcaster/host in a live-broadcast profile.
            Role_Subscriber: An audience(default) in a live-broadcast profile.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example,
            you want to access the Agora Service within 10 minutes after the token is generated,
            set token_expire as 600(seconds).
        :param privilege_expire: represented by the number of seconds elapsed since now. If, for example,
            you want to enable your privilege for 10 minutes, set privilege_expire as 600(seconds).
        :return: The RTC token.
        """
        return RtcTokenBuilder.build_token_with_user_account(app_id, app_certificate, channel_name, uid, role,
                                                             token_expire, privilege_expire)

    @staticmethod
    def build_token_with_user_account(app_id, app_certificate, channel_name, account, role, token_expire,
                                      privilege_expire=0):
        """
        Build the RTC token with account.
        :param app_id: The App ID issued to you by Agora. Apply for a new App ID from Agora Dashboard if it is missing
            from your kit. See Get an App ID.
        :param app_certificate: Certificate of the application that you registered in the Agora Dashboard.
            See Get an App Certificate.
        :param channel_name: Unique channel name for the AgoraRTC session in the string format.
        :param account: The user's account, max length is 255 Bytes.
        :param role: Role_Publisher: A broadcaster/host in a live-broadcast profile.
            Role_Subscriber: An audience(default) in a live-broadcast profile.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example,
            you want to access the Agora Service within 10 minutes after the token is generated,
            set token_expire as 600(seconds).
        :param privilege_expire: represented by the number of seconds elapsed since now. If, for example,
            you want to enable your privilege for 10 minutes, set privilege_expire as 600(seconds).
        :return: The RTC token.
        """
        token = AccessToken(app_id, app_certificate, expire=token_expire)

        rtc_service = ServiceRtc(channel_name, account)
        rtc_service.add_privilege(
            ServiceRtc.kPrivilegeJoinChannel, privilege_expire)
        if role == Role_Publisher:
            rtc_service.add_privilege(
                ServiceRtc.kPrivilegePublishAudioStream, privilege_expire)
            rtc_service.add_privilege(
                ServiceRtc.kPrivilegePublishVideoStream, privilege_expire)
            rtc_service.add_privilege(
                ServiceRtc.kPrivilegePublishDataStream, privilege_expire)

        token.add_service(rtc_service)
        return token.build()

    @staticmethod
    def build_token_with_uid_and_privilege(app_id, app_certificate, channel_name, uid, token_expire,
                                           join_channel_privilege_expire, pub_audio_privilege_expire,
                                           pub_video_privilege_expire, pub_data_stream_privilege_expire):
        """
        Generates an RTC token with the specified privilege.
                This method supports generating a token with the following privileges:
        - Joining an RTC channel.
        - Publishing audio in an RTC channel.
        - Publishing video in an RTC channel.
        - Publishing data streams in an RTC channel.
                The privileges for publishing audio, video, and data streams in an RTC channel apply only if you have
        enabled co-host authentication.
                A user can have multiple privileges. Each privilege is valid for a maximum of 24 hours.
        The SDK triggers the onTokenPrivilegeWillExpire and onRequestToken callbacks when the token is about to expire
        or has expired. The callbacks do not report the specific privilege affected, and you need to maintain
        the respective timestamp for each privilege in your app logic. After receiving the callback, you need
        to generate a new token, and then call renewToken to pass the new token to the SDK, or call joinChannel to re-join
        the channel.
                @note
        Agora recommends setting a reasonable timestamp for each privilege according to your scenario.
        Suppose the expiration timestamp for joining the channel is set earlier than that for publishing audio.
        When the token for joining the channel expires, the user is immediately kicked off the RTC channel
        and cannot publish any audio stream, even though the timestamp for publishing audio has not expired.
                :param app_id The App ID of your Agora project.
        :param app_certificate: The App Certificate of your Agora project.
        :param channel_name: The unique channel name for the Agora RTC session in string format. The string length must be less than 64 bytes. The channel name may contain the following characters:
        - All lowercase English letters: a to z.
        - All uppercase English letters: A to Z.
        - All numeric characters: 0 to 9.
        - The space character.
        - "!", "#", "$", "%", "&", "(", ")", "+", "-", ":", ";", "<", "=", ".", ">", "?", "@", "[", "]", "^", "_", " {", "}", "|", "~", ",".
        :param uid: The user ID. A 32-bit unsigned integer with a value range from 1 to (2^32 - 1). It must be unique. Set uid as 0, if you do not want to authenticate the user ID, that is, any uid from the app client can join the channel.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example, you want to access the
        Agora Service within 10 minutes after the token is generated, set token_expire as 600(seconds).
        :param join_channel_privilege_expire: The Unix timestamp when the privilege for joining the channel expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set join_channel_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes.
        :param pub_audio_privilege_expire: The Unix timestamp when the privilege for publishing audio expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_audio_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_audio_privilege_expire as the current Unix timestamp.
        :param pub_video_privilege_expire: The Unix timestamp when the privilege for publishing video expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_video_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_video_privilege_expire as the current Unix timestamp.
        :param pub_data_stream_privilege_expire: The Unix timestamp when the privilege for publishing data streams expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_data_stream_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_data_stream_privilege_expire as the current Unix timestamp.
        :return: The new Token
        """
        return RtcTokenBuilder.build_token_with_user_account_and_privilege(
            app_id, app_certificate, channel_name, uid, token_expire, join_channel_privilege_expire,
            pub_audio_privilege_expire, pub_video_privilege_expire, pub_data_stream_privilege_expire)

    @staticmethod
    def build_token_with_user_account_and_privilege(app_id, app_certificate, channel_name, account, token_expire,
                                                    join_channel_privilege_expire, pub_audio_privilege_expire,
                                                    pub_video_privilege_expire, pub_data_stream_privilege_expire):
        """
        Generates an RTC token with the specified privilege.

        This method supports generating a token with the following privileges:
        - Joining an RTC channel.
        - Publishing audio in an RTC channel.
        - Publishing video in an RTC channel.
        - Publishing data streams in an RTC channel.

        The privileges for publishing audio, video, and data streams in an RTC channel apply only if you have
        enabled co-host authentication.

        A user can have multiple privileges. Each privilege is valid for a maximum of 24 hours.
        The SDK triggers the onTokenPrivilegeWillExpire and onRequestToken callbacks when the token is about to expire
        or has expired. The callbacks do not report the specific privilege affected, and you need to maintain
        the respective timestamp for each privilege in your app logic. After receiving the callback, you need
        to generate a new token, and then call renewToken to pass the new token to the SDK, or call joinChannel to re-join
        the channel.

        @note
        Agora recommends setting a reasonable timestamp for each privilege according to your scenario.
        Suppose the expiration timestamp for joining the channel is set earlier than that for publishing audio.
        When the token for joining the channel expires, the user is immediately kicked off the RTC channel
        and cannot publish any audio stream, even though the timestamp for publishing audio has not expired.

        :param app_id: The App ID of your Agora project.
        :param app_certificate: The App Certificate of your Agora project.
        :param channel_name: The unique channel name for the Agora RTC session in string format. The string length must be less than 64 bytes. The channel name may contain the following characters:
        - All lowercase English letters: a to z.
        - All uppercase English letters: A to Z.
        - All numeric characters: 0 to 9.
        - The space character.
        - "!", "#", "$", "%", "&", "(", ")", "+", "-", ":", ";", "<", "=", ".", ">", "?", "@", "[", "]", "^", "_", " {", "}", "|", "~", ",".
        :param account: The user account.
        :param token_expire: represented by the number of seconds elapsed since now. If, for example, you want to access the
        Agora Service within 10 minutes after the token is generated, set token_expire as 600(seconds).
        :param join_channel_privilege_expire: The Unix timestamp when the privilege for joining the channel expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set join_channel_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes.
        :param pub_audio_privilege_expire: The Unix timestamp when the privilege for publishing audio expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_audio_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_audio_privilege_expire as the current Unix timestamp.
        :param pub_video_privilege_expire: The Unix timestamp when the privilege for publishing video expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_video_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_video_privilege_expire as the current Unix timestamp.
        :param pub_data_stream_privilege_expire: The Unix timestamp when the privilege for publishing data streams expires, represented
        by the sum of the current timestamp plus the valid time period of the token. For example, if you set pub_data_stream_privilege_expire as the
        current timestamp plus 600 seconds, the token expires in 10 minutes. If you do not want to enable this privilege,
        set pub_data_stream_privilege_expire as the current Unix timestamp.
        :return: The new Token
        """
        token = AccessToken(app_id, app_certificate, expire=token_expire)

        service_rtc = ServiceRtc(channel_name, account)
        service_rtc.add_privilege(
            ServiceRtc.kPrivilegeJoinChannel, join_channel_privilege_expire)
        service_rtc.add_privilege(
            ServiceRtc.kPrivilegePublishAudioStream, pub_audio_privilege_expire)
        service_rtc.add_privilege(
            ServiceRtc.kPrivilegePublishVideoStream, pub_video_privilege_expire)
        service_rtc.add_privilege(
            ServiceRtc.kPrivilegePublishDataStream, pub_data_stream_privilege_expire)
        token.add_service(service_rtc)

        return token.build()
