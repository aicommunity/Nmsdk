object StatisticForm: TStatisticForm
  Left = 0
  Top = 0
  Caption = 'StatisticForm'
  ClientHeight = 347
  ClientWidth = 176
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 176
    Height = 306
    Align = alClient
    TabOrder = 0
    ExplicitLeft = 144
    ExplicitTop = 64
    ExplicitWidth = 185
    ExplicitHeight = 41
    object AngleMaxRangeLabeledEdit: TLabeledEdit
      Left = 8
      Top = 24
      Width = 137
      Height = 21
      EditLabel.Width = 81
      EditLabel.Height = 13
      EditLabel.Caption = 'Angle max range'
      TabOrder = 0
    end
    object MaxSpeedLabeledEdit: TLabeledEdit
      Left = 8
      Top = 104
      Width = 137
      Height = 21
      EditLabel.Width = 52
      EditLabel.Height = 13
      EditLabel.Caption = 'Max speed'
      TabOrder = 1
    end
    object MaxFrequencyLabeledEdit: TLabeledEdit
      Left = 8
      Top = 191
      Width = 137
      Height = 21
      EditLabel.Width = 72
      EditLabel.Height = 13
      EditLabel.Caption = 'Max frequency'
      TabOrder = 2
    end
    object AvgSpeedLabeledEdit: TLabeledEdit
      Left = 8
      Top = 144
      Width = 137
      Height = 21
      EditLabel.Width = 51
      EditLabel.Height = 13
      EditLabel.Caption = 'Avg speed'
      TabOrder = 3
    end
    object AngleAvgRangeLabeledEdit: TLabeledEdit
      Left = 8
      Top = 64
      Width = 137
      Height = 21
      EditLabel.Width = 79
      EditLabel.Height = 13
      EditLabel.Caption = 'Angle avg range'
      TabOrder = 4
    end
  end
  object Panel2: TPanel
    Left = 0
    Top = 306
    Width = 176
    Height = 41
    Align = alBottom
    TabOrder = 1
    ExplicitLeft = 208
    ExplicitTop = 136
    ExplicitWidth = 185
    object Button1: TButton
      Left = 8
      Top = 6
      Width = 75
      Height = 25
      Caption = 'Reset'
      TabOrder = 0
      OnClick = Button1Click
    end
  end
end
