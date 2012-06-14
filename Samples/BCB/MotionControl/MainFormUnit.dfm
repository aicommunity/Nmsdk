object MainForm: TMainForm
  Left = 0
  Top = 0
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
    object ShowClassesButton: TButton
      Left = 8
      Top = 8
      Width = 169
      Height = 25
      Caption = 'Show Classes'
      TabOrder = 0
      OnClick = ShowClassesButtonClick
    end
    object CreateModelButton: TButton
      Left = 8
      Top = 39
      Width = 169
      Height = 25
      Caption = 'Create Model'
      TabOrder = 1
      OnClick = CreateModelButtonClick
    end
    object DestroyModelButton: TButton
      Left = 8
      Top = 68
      Width = 169
      Height = 25
      Caption = 'Destroy Model'
      TabOrder = 2
      OnClick = DestroyModelButtonClick
    end
    object StartButton: TButton
      Left = 8
      Top = 99
      Width = 169
      Height = 25
      Caption = 'Start'
      TabOrder = 3
      OnClick = StartButtonClick
    end
    object StopButton: TButton
      Left = 8
      Top = 130
      Width = 169
      Height = 25
      Caption = 'Stop'
      TabOrder = 4
      OnClick = StopButtonClick
    end
    object ResetButton: TButton
      Left = 8
      Top = 161
      Width = 169
      Height = 25
      Caption = 'Reset'
      TabOrder = 5
      OnClick = ResetButtonClick
    end
    object Button1: TButton
      Left = 8
      Top = 233
      Width = 169
      Height = 25
      Caption = 'Update'
      TabOrder = 6
      OnClick = Button1Click
    end
  end
  object Button: TButton
    Left = 48
    Top = 8
    Width = 75
    Height = 25
    Caption = 'Button'
    TabOrder = 1
    OnClick = ButtonClick
  end
  object Button2: TButton
    Left = 48
    Top = 39
    Width = 75
    Height = 25
    Caption = 'Button'
    TabOrder = 2
    OnClick = Button2Click
  end
  object Timer: TTimer
    Enabled = False
    Interval = 1
    OnTimer = TimerTimer
    Left = 16
    Top = 8
  end
end
