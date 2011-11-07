object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 
    #1069#1082#1089#1090#1088#1072#1087#1086#1083#1103#1090#1086#1088' (c) S.P.Romanov, A.V.Bakhshiev, 2010 (www.ailab.ru' +
    ')'
  ClientHeight = 324
  ClientWidth = 713
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  inline WatchFrame: TWatchFrame
    Left = 0
    Top = 0
    Width = 713
    Height = 208
    Align = alClient
    TabOrder = 0
    TabStop = True
    ExplicitWidth = 713
    ExplicitHeight = 208
    inherited Chart1: TChart
      Width = 713
      Height = 208
      ExplicitWidth = 713
      ExplicitHeight = 208
    end
  end
  object Panel1: TPanel
    Left = 0
    Top = 208
    Width = 713
    Height = 116
    Align = alBottom
    TabOrder = 1
    DesignSize = (
      713
      116)
    object Label1: TLabel
      Left = 98
      Top = 11
      Width = 189
      Height = 13
      Caption = #1040#1084#1087#1083#1080#1090#1091#1076#1072' '#1089#1080#1085#1072#1087#1089#1072' [0;10, '#1096#1072#1075' 0.001]'
    end
    object Label2: TLabel
      Left = 98
      Top = 63
      Width = 203
      Height = 13
      Caption = #1040#1088#1075#1091#1084#1077#1085#1090' '#1089#1080#1085#1072#1087#1089#1072' [0;10 '#1056#1072#1076', '#1096#1072#1075' 0.001]'
    end
    object Button1: TButton
      Left = 8
      Top = 6
      Width = 75
      Height = 25
      Caption = #1048#1084#1087#1091#1083#1100#1089
      TabOrder = 0
      OnClick = Button1Click
    end
    object AmplitudeTrackBar: TTrackBar
      Left = 89
      Top = 30
      Width = 552
      Height = 27
      Anchors = [akLeft, akTop, akRight]
      Max = 10000
      Position = 1000
      TabOrder = 1
      OnChange = AmplitudeTrackBarChange
    end
    object AmplitudeEdit: TEdit
      Left = 647
      Top = 32
      Width = 57
      Height = 21
      Anchors = [akTop, akRight]
      Color = clBtnFace
      ReadOnly = True
      TabOrder = 2
      Text = '1'
    end
    object FrequencyTrackBar: TTrackBar
      Left = 89
      Top = 82
      Width = 552
      Height = 27
      Anchors = [akLeft, akTop, akRight]
      Max = 10000
      Position = 1000
      TabOrder = 3
      OnChange = FrequencyTrackBarChange
    end
    object FrequencyEdit: TEdit
      Left = 647
      Top = 84
      Width = 57
      Height = 21
      Anchors = [akTop, akRight]
      Color = clBtnFace
      ReadOnly = True
      TabOrder = 4
      Text = '1'
    end
    object ResetButton: TButton
      Left = 8
      Top = 37
      Width = 75
      Height = 25
      Caption = #1057#1073#1088#1086#1089
      TabOrder = 5
      OnClick = ResetButtonClick
    end
  end
  object Timer: TTimer
    Interval = 1
    OnTimer = TimerTimer
    Left = 120
    Top = 16
  end
end
