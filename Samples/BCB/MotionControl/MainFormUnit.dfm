object MainForm: TMainForm
  Left = 0
  Top = 100
  Caption = 'MainForm'
  ClientHeight = 266
  ClientWidth = 527
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poDesigned
  Visible = True
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Panel1: TPanel
    Left = 342
    Top = 0
    Width = 185
    Height = 266
    Align = alRight
    TabOrder = 0
    object Button2: TButton
      Left = 8
      Top = 39
      Width = 169
      Height = 25
      Caption = 'Manipulator Control'
      TabOrder = 0
      OnClick = Button2Click
    end
    object Button: TButton
      Left = 8
      Top = 8
      Width = 169
      Height = 25
      Caption = 'Engine Control'
      TabOrder = 1
      OnClick = ButtonClick
    end
  end
  object Timer: TTimer
    Enabled = False
    Interval = 1
    Left = 224
    Top = 24
  end
end
