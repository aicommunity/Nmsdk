object NEnsembleControlFrame: TNEnsembleControlFrame
  Left = 0
  Top = 0
  Width = 678
  Height = 495
  DoubleBuffered = True
  ParentDoubleBuffered = False
  TabOrder = 0
  object Splitter2: TSplitter
    Left = 0
    Top = 265
    Width = 678
    Height = 16
    Cursor = crVSplit
    Align = alTop
    Color = clInactiveBorder
    ParentColor = False
    ExplicitTop = 317
  end
  object Panel2: TPanel
    Left = 0
    Top = 0
    Width = 678
    Height = 265
    Align = alTop
    TabOrder = 0
    object Splitter1: TSplitter
      Left = 331
      Top = 1
      Width = 15
      Height = 171
      Color = clInactiveBorder
      ParentColor = False
      ExplicitLeft = 1
      ExplicitHeight = 676
    end
    object GroupBox1: TGroupBox
      Left = 1
      Top = 1
      Width = 330
      Height = 171
      Align = alLeft
      Caption = ' '#1057#1087#1080#1089#1086#1082' '#1073#1077#1090#1072'-'#1072#1085#1089#1072#1084#1073#1083#1077#1081' '
      DoubleBuffered = True
      ParentDoubleBuffered = False
      TabOrder = 0
      ExplicitHeight = 223
      object BetaEnsembleStringGrid: TStringGrid
        Left = 2
        Top = 15
        Width = 326
        Height = 154
        Align = alClient
        DefaultColWidth = 40
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goColSizing]
        TabOrder = 0
        ExplicitWidth = 672
        ExplicitHeight = 168
      end
    end
    object GroupBox3: TGroupBox
      Left = 346
      Top = 1
      Width = 331
      Height = 171
      Align = alClient
      Caption = ' '#1057#1087#1080#1089#1086#1082' '#1072#1085#1089#1072#1084#1073#1083#1077#1081' '
      DoubleBuffered = True
      ParentDoubleBuffered = False
      TabOrder = 1
      ExplicitLeft = 1
      ExplicitTop = 191
      ExplicitWidth = 676
      ExplicitHeight = 124
      object EnsembleStringGrid: TStringGrid
        Left = 2
        Top = 15
        Width = 327
        Height = 154
        Align = alClient
        DefaultColWidth = 40
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goColSizing]
        TabOrder = 0
        ExplicitWidth = 672
        ExplicitHeight = 107
      end
    end
    object Panel1: TPanel
      Left = 1
      Top = 172
      Width = 676
      Height = 92
      Align = alBottom
      TabOrder = 2
      object GroupBox2: TGroupBox
        Left = 1
        Top = 1
        Width = 674
        Height = 48
        Align = alTop
        Caption = 
          ' '#1055#1086#1088#1086#1075' '#1087#1088#1077#1074#1099#1096#1077#1085#1080#1103' '#1089#1090#1072#1090#1080#1095#1077#1089#1082#1086#1081' '#1082#1086#1084#1087#1086#1085#1077#1085#1090#1086#1081' '#1089#1074#1103#1079#1080' '#1085#1072#1095#1072#1083#1072' '#1086#1090#1089#1095#1077#1090#1072' (' +
          #1089#1084' '#1085#1080#1078#1077') '
        TabOrder = 0
        DesignSize = (
          674
          48)
        object EnsembleThresholdTrackBar: TTrackBar
          Left = 1
          Top = 14
          Width = 612
          Height = 27
          Anchors = [akLeft, akTop, akRight]
          Max = 10000
          TabOrder = 0
          OnChange = EnsembleThresholdTrackBarChange
        end
        object EnsembleThresholdEdit: TEdit
          Left = 614
          Top = 16
          Width = 49
          Height = 21
          Anchors = [akTop, akRight]
          TabOrder = 1
          Text = '0'
          OnChange = EnsembleThresholdEditChange
        end
      end
      object EnsembleThresholdModeRadioGroup: TRadioGroup
        Left = 1
        Top = 49
        Width = 674
        Height = 42
        Align = alClient
        Caption = 
          ' '#1053#1072#1095#1072#1083#1086' '#1086#1090#1089#1095#1077#1090#1072' '#1076#1083#1103' '#1076#1086#1073#1072#1074#1083#1077#1085#1080#1103' '#1085#1077#1081#1088#1086#1085#1072' '#1074' '#1072#1085#1089#1072#1084#1073#1083#1100' '#1087#1086' '#1087#1088#1077#1074#1099#1096#1077#1085#1080#1102' ' +
          #1087#1086#1088#1086#1075#1072' '
        Columns = 3
        ItemIndex = 0
        Items.Strings = (
          #1053#1091#1083#1100
          #1057#1088#1077#1076#1085#1077#1077' Gs '#1089#1080#1085#1072#1087#1089#1086#1074' '#1085#1077#1081#1088#1086#1085#1072
          #1057#1088#1077#1076#1085#1077#1077' Gs '#1089#1080#1085#1072#1087#1089#1086#1074' '#1089#1077#1090#1080)
        TabOrder = 1
        WordWrap = True
        OnClick = EnsembleThresholdModeRadioGroupClick
      end
    end
  end
  object Panel3: TPanel
    Left = 0
    Top = 281
    Width = 678
    Height = 214
    Align = alClient
    TabOrder = 1
    ExplicitLeft = 104
    ExplicitTop = 312
    ExplicitWidth = 409
    ExplicitHeight = 86
    object GroupBox4: TGroupBox
      Left = 1
      Top = 1
      Width = 676
      Height = 212
      Align = alClient
      Caption = ' '#1057#1087#1080#1089#1086#1082' '#1089#1074#1103#1079#1077#1081' '#1084#1077#1078#1076#1091' '#1072#1085#1089#1072#1084#1073#1083#1103#1084#1080' '
      DoubleBuffered = True
      ParentDoubleBuffered = False
      TabOrder = 0
      ExplicitWidth = 336
      ExplicitHeight = 375
      object EnsembleLinksStringGrid: TStringGrid
        Left = 2
        Top = 15
        Width = 672
        Height = 195
        Align = alClient
        DefaultColWidth = 40
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goColSizing]
        TabOrder = 0
        ExplicitLeft = 3
        ExplicitTop = 13
        ExplicitHeight = 159
      end
    end
  end
end
