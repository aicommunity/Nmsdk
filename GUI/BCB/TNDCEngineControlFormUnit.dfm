object NDCEngineControlForm: TNDCEngineControlForm
  Left = 0
  Top = 0
  Caption = 'NDCEngineControlForm'
  ClientHeight = 448
  ClientWidth = 722
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
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 256
    Height = 248
    Align = alClient
    TabOrder = 0
    object GroupBox1: TGroupBox
      Left = 1
      Top = 1
      Width = 254
      Height = 246
      Align = alClient
      Caption = ' Visual '
      TabOrder = 0
      object Image: TImage
        Left = 2
        Top = 15
        Width = 250
        Height = 229
        Align = alClient
        Stretch = True
        ExplicitLeft = 64
        ExplicitTop = 72
        ExplicitWidth = 105
        ExplicitHeight = 105
      end
    end
  end
  object Panel2: TPanel
    Left = 0
    Top = 248
    Width = 722
    Height = 200
    Align = alBottom
    TabOrder = 1
  end
  object Panel3: TPanel
    Left = 256
    Top = 0
    Width = 466
    Height = 248
    Align = alRight
    TabOrder = 2
    object IaCheckBox: TCheckBox
      Left = 6
      Top = 16
      Width = 305
      Height = 17
      Caption = #1054#1057' '#1087#1086' '#1091#1075#1083#1086#1074#1086#1081' '#1089#1082#1086#1088#1086#1089#1090#1080' (Ia) '
      Checked = True
      State = cbChecked
      TabOrder = 0
      OnClick = IaCheckBoxClick
    end
    object IbCheckBox: TCheckBox
      Left = 6
      Top = 39
      Width = 305
      Height = 17
      Caption = #1054#1057' '#1087#1086' '#1082#1088#1091#1090#1103#1097#1077#1084#1091' '#1084#1086#1084#1077#1085#1090#1091' (Ib) '
      TabOrder = 1
      OnClick = IbCheckBoxClick
    end
    object IICheckBox: TCheckBox
      Left = 6
      Top = 62
      Width = 305
      Height = 17
      Caption = #1054#1057' '#1087#1086' '#1091#1075#1083#1091' (II) '
      Checked = True
      State = cbChecked
      TabOrder = 2
      OnClick = IICheckBoxClick
    end
    object ControlVoltageCheckBox: TCheckBox
      Left = 6
      Top = 85
      Width = 181
      Height = 17
      Caption = #1059#1087#1088#1072#1074#1083#1103#1102#1097#1077#1077' '#1074#1086#1079#1076#1077#1081#1089#1090#1074#1080#1077' (U) '
      Checked = True
      State = cbChecked
      TabOrder = 3
      OnClick = ControlVoltageCheckBoxClick
    end
    object GroupBox2: TGroupBox
      Left = 6
      Top = 160
      Width = 451
      Height = 82
      Caption = ' '#1042#1085#1077#1096#1085#1080#1081' '#1084#1086#1084#1077#1085#1090' '#1085#1072' '#1084#1086#1076#1077#1083#1080' '#1076#1074#1080#1075#1072#1090#1077#1083#1103' '
      TabOrder = 4
      object MomentTrackBar: TTrackBar
        Left = 5
        Top = 18
        Width = 443
        Height = 27
        Max = 1000
        Min = -1000
        TabOrder = 0
        OnChange = MomentTrackBarChange
      end
      object MomentProgressBar: TProgressBar
        Left = 13
        Top = 53
        Width = 349
        Height = 17
        Max = 1000
        TabOrder = 1
      end
      object ExtMomentEdit: TEdit
        Left = 368
        Top = 51
        Width = 73
        Height = 21
        Color = clBtnFace
        ReadOnly = True
        TabOrder = 2
        Text = '0'
      end
    end
  end
end
