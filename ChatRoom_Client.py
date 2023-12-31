#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@File    :ChatRoom_Client.py
@Author  :Sunshine
@Date    :16/11/2023 14:34
'''
import wx
from socket import *
import threading


class ChatRoomClient(wx.Frame):
    def __init__(self, c_name):
        wx.Frame.__init__(self,
                          None,
                          id=101,
                          title='Chat Room - Member : %s' % c_name,
                          pos=wx.DefaultPosition,
                          size=(400, 470),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER))
        pl = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        g1 = wx.FlexGridSizer(wx.HORIZONTAL)

        # Create Two buttons Join & Leave
        btn_conn = wx.Button(pl, size=(200, 40), label='Join')
        btn_dis_conn = wx.Button(pl, size=(200, 40), label='Leave')
        g1.Add(btn_conn, 1, wx.TOP | wx.LEFT)
        g1.Add(btn_dis_conn, 1, wx.TOP | wx.RIGHT)
        box.Add(g1, 1, wx.ALIGN_CENTRE)

        self.show_text = wx.TextCtrl(pl, size=(400, 250), style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 1, wx.ALIGN_CENTRE)

        # Create input box
        self.input_text = wx.TextCtrl(pl, size=(400, 100), style=wx.TE_MULTILINE)
        box.Add(self.input_text, 1, wx.ALIGN_CENTER)

        # Create Two buttons Send & Reset
        g2 = wx.FlexGridSizer(wx.HORIZONTAL)
        btn_send = wx.Button(pl, size=(200, 40), label='Send')
        btn_reset = wx.Button(pl, size=(200, 40), label='Reset')
        g2.Add(btn_reset, 1, wx.TOP | wx.LEFT)
        g2.Add(btn_send, 1, wx.TOP | wx.RIGHT)
        box.Add(g2, 1, wx.ALIGN_CENTER)

        pl.SetSizer(box)
        ''' The above code is the client window layout '''

        ''' Bind click events to all buttons'''
        self.Bind(wx.EVT_BUTTON, self.connect_to_sever, btn_conn)
        self.Bind(wx.EVT_BUTTON, self.send_to_sever, btn_send)
        self.Bind(wx.EVT_BUTTON, self.go_out, btn_dis_conn)
        self.Bind(wx.EVT_BUTTON, self.reset, btn_reset)

        self.name = c_name
        self.isConnected = False
        self.client_socket = None

    def connect_to_sever(self, event):
        print('Client %s start to connect to sever' % self.name)
        if not self.isConnected:
            server_host_port = ('localhost', 8888)
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(server_host_port)
            # It is stipulated that as long as the client connects successfully, it will immediately send its name to the server.
            self.client_socket.send(self.name.encode('utf-8'))
            t = threading.Thread(target=self.receive_data)
            t.setDaemon(True)
            self.isConnected = True
            t.start()

    # Receive chat data initiated by the server
    def receive_data(self):
        print('Client prepare to receive data from sever')
        while self.isConnected:
            data = self.client_socket.recv(1024).decode('utf-8')
            if data == 'A^disconnect^B':
                # Handle server-initiated disconnect signal
                self.isConnected = False
                # Close the client window
                self.close_window_signal()
            else:
                self.show_text.AppendText("%s\n" % data)

    # Client sends message to chat room
    def send_to_sever(self, event):
        if self.isConnected:
            info = self.input_text.GetValue()
            if info != '':
                self.client_socket.send(info.encode('utf-8'))
                self.input_text.SetValue('')

    # Client leaves chat room
    def go_out(self, event):
        self.client_socket.send('A^disconnect^B'.encode('utf-8'))
        self.isConnected = False
        self.close_window_signal()

    # Resetting the client input text box
    def reset(self, event):
        self.input_text.Clear()

    def close_window_signal(self):
        wx.CallAfter(self.Destroy)


if __name__ == '__main__':
    app = wx.App()
    name = input("Please enter client's name: ")
    ChatRoomClient(name).Show()
    app.MainLoop()
