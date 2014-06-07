object NNewPositionControlElementForm: TNNewPositionControlElementForm
  Left = 0
  Top = 0
  Caption = 'NNewPositionControlElementForm'
  ClientHeight = 459
  ClientWidth = 704
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Splitter1: TSplitter
    Left = 0
    Top = 105
    Width = 704
    Height = 15
    Cursor = crVSplit
    Align = alTop
    ExplicitLeft = 16
    ExplicitTop = 99
  end
  object GroupBox1: TGroupBox
    Left = 0
    Top = 0
    Width = 704
    Height = 105
    Align = alTop
    Caption = ' Current recognized state '
    TabOrder = 0
    ExplicitLeft = 216
    ExplicitTop = 104
    ExplicitWidth = 185
    object TrainedStateStringGrid: TStringGrid
      Left = 2
      Top = 15
      Width = 700
      Height = 88
      Align = alClient
      DefaultRowHeight = 18
      TabOrder = 0
      ExplicitLeft = 3
      ExplicitTop = 11
    end
  end
  object GroupBox2: TGroupBox
    Left = 0
    Top = 120
    Width = 704
    Height = 105
    Align = alTop
    Caption = ' Current selected state '
    TabOrder = 1
    ExplicitTop = 8
    object SelectedStateStringGrid: TStringGrid
      Left = 2
      Top = 15
      Width = 700
      Height = 88
      Align = alClient
      DefaultRowHeight = 18
      Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goEditing]
      TabOrder = 0
      OnSetEditText = SelectedStateStringGridSetEditText
      ExplicitLeft = 368
      ExplicitTop = 48
      ExplicitWidth = 320
      ExplicitHeight = 120
    end
  end
  object TrainPositionButton: TButton
    Left = 8
    Top = 231
    Width = 75
    Height = 25
    Caption = 'Train Position'
    TabOrder = 2
    OnClick = TrainPositionButtonClick
  end
end
