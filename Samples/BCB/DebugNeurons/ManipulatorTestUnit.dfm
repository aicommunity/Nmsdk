object ManipulatorTestForm: TManipulatorTestForm
  Left = 0
  Top = 0
  Caption = 'ManipulatorTestForm'
  ClientHeight = 423
  ClientWidth = 530
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
  object Image: TImage
    Left = 0
    Top = 0
    Width = 530
    Height = 304
    Align = alClient
    Center = True
    IncrementalDisplay = True
    Proportional = True
    ExplicitLeft = 128
    ExplicitTop = 56
    ExplicitWidth = 105
    ExplicitHeight = 105
  end
  object Panel1: TPanel
    Left = 0
    Top = 304
    Width = 530
    Height = 119
    Align = alBottom
    TabOrder = 0
    object Label1: TLabel
      Left = 8
      Top = 51
      Width = 38
      Height = 13
      Caption = #1052#1086#1084#1077#1085#1090
    end
    object TrackBar: TTrackBar
      Left = 0
      Top = 6
      Width = 530
      Height = 27
      Max = 1000
      TabOrder = 0
      OnChange = TrackBarChange
    end
    object MomentTrackBar: TTrackBar
      Left = 0
      Top = 70
      Width = 249
      Height = 27
      Max = 1000
      Min = -1000
      TabOrder = 1
      OnChange = MomentTrackBarChange
    end
    object MomentProgressBar: TProgressBar
      Left = 255
      Top = 72
      Width = 266
      Height = 17
      Max = 1000
      TabOrder = 2
    end
  end
end
