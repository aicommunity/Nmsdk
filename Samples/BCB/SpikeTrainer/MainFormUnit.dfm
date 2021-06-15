object MainForm: TMainForm
  Left = 800
  Top = 0
  Caption = 'MainForm'
  ClientHeight = 75
  ClientWidth = 182
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
    Left = -3
    Top = 0
    Width = 185
    Height = 75
    Align = alRight
    TabOrder = 0
    ExplicitLeft = 342
    ExplicitHeight = 266
    object Button2: TButton
      Left = 8
      Top = 23
      Width = 169
      Height = 25
      Caption = 'Manipulator Control'
      TabOrder = 0
      OnClick = Button2Click
    end
  end
  object Timer: TTimer
    Enabled = False
    Interval = 1
    Left = 24
    Top = 8
  end
end
