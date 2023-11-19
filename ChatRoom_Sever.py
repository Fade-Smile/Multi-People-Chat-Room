#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@File    :ChatRoom_Sever.py
@Author  :Sunshine
@Date    :16/11/2023 14:34
'''

import wx
from socket import *
import threading
import time


class ChatRoomServer(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,
                          None,
                          id=102,  #
                          title='Chat Room - Sever Side Interface',
                          pos=wx.DefaultPosition,
                          size=(400, 470),
                          style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER))
        pl = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        g1 = wx.FlexGridSizer(wx.HORIZONTAL)
        # Create three buttons Start, Save and Quit
        btn_start_sever = wx.Button(pl, size=(130, 40), label='Start')
        btn_save_record = wx.Button(pl, size=(130, 40), label='Save Record')
        btn_stop_sever = wx.Button(pl, size=(130, 40), label='Quit')
        g1.Add(btn_start_sever, 1, wx.TOP)
        g1.Add(btn_save_record, 1, wx.TOP)
        g1.Add(btn_stop_sever, 1, wx.TOP)
        box.Add(g1, 1, wx.ALIGN_CENTRE)

        # Create a read-only text box to display read-only chat history
        self.show_text = wx.TextCtrl(pl, size=(400, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 1, wx.ALIGN_CENTRE)
        pl.SetSizer(box)
        ''' The above code is the server window layout '''

        ''' Some attributes that the server is prepared to execute '''
        self.isOn = False
        self.host_port = ("", 8888)
        self.sever_socket = socket(AF_INET, SOCK_STREAM)
        self.sever_socket.bind(self.host_port)
        self.sever_socket.listen(5)
        self.session_thread_map = {}

        ''' Bind corresponding functions to all buttons '''
        self.Bind(wx.EVT_BUTTON, self.start_sever, btn_start_sever)
        self.Bind(wx.EVT_BUTTON, self.save_record, btn_save_record)
        self.Bind(wx.EVT_BUTTON, self.quit, btn_stop_sever)

    def start_sever(self, event):
        print('The Sever Starts!')
        if not self.isOn:
            self.isOn = True
            main_thread = threading.Thread(target=self.do_word)
            main_thread.setDaemon(True)
            main_thread.start()

    def do_word(self):
        print('The Sever starts Working')
        while self.isOn:
            session_socket, client_addr = self.sever_socket.accept()
            username = session_socket.recv(1024).decode('UTF-8')
            session_thread = SessionThread(session_socket, username, self)
            self.session_thread_map[username] = session_thread
            session_thread.start()
            self.show_info_and_send_to_all_clients('Sever Notification',
                                                   'Welcome %s join the Chat Room!' % username,
                                                   time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.sever_socket.close()

    def show_info_and_send_to_all_clients(self, source, data, data_time):

        send_data = '%s : %s \n Time: %s \n' % (source, data, data_time)
        self.show_text.AppendText('-------------------------------------\n %s' % send_data)
        for client in self.session_thread_map.values():
            if client.isOn:
                client.user_socket.send(send_data.encode('utf-8'))

    def save_record(self, event):
        record = self.show_text.GetValue()
        with open('record.log', 'w+') as f:
            f.write(record)

    def quit(self, event):
        self.show_info_and_send_to_all_clients('Sever Notification',
                                               'The server is going to be closed shortly!',
                                               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        for client in self.session_thread_map.values():
            if client.isOn:
                client.user_socket.send('A^disconnect^B'.encode('utf-8'))

        time.sleep(1)

        for client in self.session_thread_map.values():
            if client.isOn:
                client.isOn = False
                client.user_socket.close()

        self.isOn = False
        self.sever_socket.close()
        self.close_window()

    def close_window(self):
        self.Close()

    def close_client_window(self, client_thread):
        wx.CallAfter(client_thread.close_window_signal)

class SessionThread(threading.Thread):

    def __init__(self, user_socket, username, server):
        threading.Thread.__init__(self)
        self.user_socket = user_socket
        self.username = username
        self.server = server
        self.isOn = True

    def run(self):
        print('Client %s connect with sever successfully, the sever starts a session thread' % self.username)
        while self.isOn:
            data = self.user_socket.recv(1024).decode('utf-8')
            if data == 'A^disconnect^B':
                self.isOn = False
                self.server.show_info_and_send_to_all_clients('Sever Notification',
                                                              '%s has left the Chat Room!' % self.username,
                                                              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                self.server.close_client_window(self)
            else:
                self.server.show_info_and_send_to_all_clients(self.username,
                                                              data,
                                                              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.user_socket.close()


if __name__ == '__main__':
    app = wx.App()
    ChatRoomServer().Show()
    app.MainLoop()
