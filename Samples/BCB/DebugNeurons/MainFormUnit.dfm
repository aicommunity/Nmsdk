object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 'MainForm'
  ClientHeight = 319
  ClientWidth = 858
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  OldCreateOrder = False
  Position = poDesigned
  OnClose = FormClose
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    Left = 0
    Top = 41
    Width = 225
    Height = 278
    Align = alLeft
    Caption = ' '#1057#1086#1076#1077#1088#1078#1080#1084#1086#1077' '#1084#1086#1076#1077#1083#1080' '
    TabOrder = 0
    object StringGrid1: TStringGrid
      Left = 2
      Top = 15
      Width = 221
      Height = 261
      Align = alClient
      ColCount = 2
      DefaultColWidth = 120
      FixedCols = 0
      Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goRowSelect]
      TabOrder = 0
    end
  end
  object GroupBox2: TGroupBox
    Left = 225
    Top = 41
    Width = 225
    Height = 278
    Align = alLeft
    Caption = #1057#1087#1080#1089#1086#1082' '#1085#1077#1081#1088#1086#1085#1086#1074' '#1089#1077#1090#1080
    TabOrder = 1
    object StringGrid2: TStringGrid
      Left = 2
      Top = 15
      Width = 221
      Height = 261
      Align = alClient
      ColCount = 2
      DefaultColWidth = 120
      FixedCols = 0
      Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goRowSelect]
      TabOrder = 0
      OnSelectCell = StringGrid2SelectCell
    end
  end
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 858
    Height = 41
    Align = alTop
    TabOrder = 2
    object Button2: TButton
      Left = 441
      Top = 8
      Width = 75
      Height = 25
      Caption = #1055#1088#1086#1089#1084#1086#1090#1088
      TabOrder = 0
      OnClick = Button2Click
    end
    object Button1: TButton
      Left = 522
      Top = 8
      Width = 75
      Height = 25
      Caption = 'Button1'
      TabOrder = 1
      OnClick = Button1Click
    end
    object Button3: TButton
      Left = 12
      Top = 8
      Width = 75
      Height = 25
      Caption = #1055#1091#1089#1082
      TabOrder = 2
      OnClick = Button3Click
    end
    object Button4: TButton
      Left = 93
      Top = 8
      Width = 75
      Height = 25
      Caption = #1057#1090#1086#1087
      TabOrder = 3
      OnClick = Button4Click
    end
    object Button5: TButton
      Left = 360
      Top = 8
      Width = 75
      Height = 25
      Caption = #1057#1086#1093#1088#1072#1085#1080#1090#1100
      TabOrder = 4
    end
    object Button6: TButton
      Left = 175
      Top = 8
      Width = 75
      Height = 25
      Caption = #1057#1073#1088#1086#1089
      TabOrder = 5
      OnClick = Button6Click
    end
  end
  inline ClassRegistryFrame: TUClassRegistryFrame
    Left = 450
    Top = 41
    Width = 408
    Height = 278
    Align = alClient
    TabOrder = 3
    ExplicitLeft = 341
    ExplicitTop = -92
    ExplicitWidth = 408
    ExplicitHeight = 278
    inherited Splitter: TSplitter
      Left = 118
      Height = 194
      ExplicitLeft = 118
      ExplicitHeight = 194
    end
    inherited Panel: TPanel
      Top = 219
      Width = 408
      ExplicitTop = 219
      ExplicitWidth = 408
      inherited LabeledEdit: TLabeledEdit
        Width = 292
        EditLabel.Width = 113
        EditLabel.ExplicitLeft = 8
        EditLabel.ExplicitTop = 8
        EditLabel.ExplicitWidth = 113
        ExplicitWidth = 292
      end
      inherited SetBitBtn: TBitBtn
        Left = 306
        ExplicitLeft = 306
      end
      inherited RestoreBitBtn: TBitBtn
        Left = 354
        ExplicitLeft = 354
      end
    end
    inherited ListView: TListView
      Left = 121
      Height = 194
      ExplicitLeft = 121
      ExplicitHeight = 194
    end
    inherited HeaderControl: THeaderControl
      Width = 408
      ExplicitWidth = 408
    end
    inherited ComponentsListView: TListView
      Width = 118
      Height = 194
      ExplicitWidth = 118
      ExplicitHeight = 194
    end
  end
  object Timer: TTimer
    Enabled = False
    Interval = 10
    OnTimer = TimerTimer
    Left = 16
    Top = 88
  end
end
