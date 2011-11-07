object NSourceControlFrame: TNSourceControlFrame
  Left = 0
  Top = 0
  Width = 575
  Height = 519
  TabOrder = 0
  object Splitter1: TSplitter
    Left = 0
    Top = 304
    Width = 575
    Height = 3
    Cursor = crVSplit
    Align = alBottom
    ExplicitTop = 177
    ExplicitWidth = 215
  end
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 575
    Height = 304
    Align = alClient
    TabOrder = 0
    inline SourceWatchFrame: TWatchFrame
      Left = 1
      Top = 1
      Width = 573
      Height = 302
      Align = alClient
      TabOrder = 0
      TabStop = True
      ExplicitLeft = 1
      ExplicitTop = 1
      ExplicitWidth = 573
      ExplicitHeight = 302
      inherited Chart1: TChart
        Width = 573
        Height = 302
        DepthAxis.Maximum = -0.730000000000000600
        DepthAxis.Minimum = -1.730000000000001000
        DepthTopAxis.Automatic = False
        DepthTopAxis.AutomaticMaximum = False
        DepthTopAxis.AutomaticMinimum = False
        DepthTopAxis.Maximum = 0.469999999999999900
        DepthTopAxis.Minimum = -0.530000000000000000
        LeftAxis.Automatic = False
        LeftAxis.AutomaticMinimum = False
        RightAxis.Automatic = False
        RightAxis.AutomaticMaximum = False
        RightAxis.AutomaticMinimum = False
        ExplicitWidth = 573
        ExplicitHeight = 302
      end
    end
  end
  object Panel2: TPanel
    Left = 0
    Top = 307
    Width = 575
    Height = 212
    Align = alBottom
    TabOrder = 1
    object GroupBox1: TGroupBox
      Left = 80
      Top = 64
      Width = 185
      Height = 105
      Caption = ' '#1048#1089#1090#1086#1095#1085#1080#1082#1080' '#1089#1080#1075#1085#1072#1083#1072' '
      TabOrder = 0
      object SourcesStringGrid: TStringGrid
        Left = 2
        Top = 15
        Width = 181
        Height = 88
        Align = alClient
        DoubleBuffered = True
        ParentDoubleBuffered = False
        TabOrder = 0
      end
    end
    object Panel3: TPanel
      Left = 392
      Top = 80
      Width = 197
      Height = 131
      TabOrder = 1
      object AmplitudeGroupBox: TGroupBox
        Left = 1
        Top = 1
        Width = 195
        Height = 48
        Align = alTop
        Caption = ' '#1040#1084#1087#1083#1080#1090#1091#1076#1072' '
        TabOrder = 0
        DesignSize = (
          195
          48)
        object AmplitudeTrackBar: TTrackBar
          Left = 2
          Top = 15
          Width = 143
          Height = 26
          Anchors = [akLeft, akTop, akRight]
          TabOrder = 0
          OnChange = AmplitudeTrackBarChange
        end
        object AmplitudeEdit: TEdit
          Left = 144
          Top = 15
          Width = 44
          Height = 21
          Anchors = [akTop, akRight]
          TabOrder = 1
          Text = '0'
          OnChange = AmplitudeEditChange
        end
      end
      object FrequencyGroupBox: TGroupBox
        Left = 1
        Top = 49
        Width = 195
        Height = 48
        Align = alTop
        Caption = ' '#1063#1072#1089#1090#1086#1090#1072' '
        TabOrder = 1
        DesignSize = (
          195
          48)
        object FrequencyTrackBar: TTrackBar
          Left = 2
          Top = 15
          Width = 143
          Height = 26
          Anchors = [akLeft, akTop, akRight]
          Max = 500
          TabOrder = 0
          OnChange = FrequencyTrackBarChange
        end
        object FrequencyEdit: TEdit
          Left = 144
          Top = 15
          Width = 44
          Height = 21
          Anchors = [akTop, akRight]
          TabOrder = 1
          Text = '0'
          OnChange = FrequencyEditChange
        end
      end
    end
    inline UClassRegistryFrame: TUClassRegistryFrame
      Left = 1
      Top = 1
      Width = 573
      Height = 210
      Align = alClient
      TabOrder = 2
      ExplicitLeft = 1
      ExplicitTop = 1
      ExplicitWidth = 573
      ExplicitHeight = 210
      inherited Splitter: TSplitter
        Left = 570
        Height = 126
        ExplicitLeft = 283
        ExplicitHeight = 126
      end
      inherited Panel: TPanel
        Top = 151
        Width = 573
        ExplicitTop = 151
        ExplicitWidth = 573
        inherited LabeledEdit: TLabeledEdit
          Width = 457
          OnKeyPress = UClassRegistryFrameLabeledEditKeyPress
          ExplicitWidth = 457
        end
        inherited SetBitBtn: TBitBtn
          Left = 471
          OnClick = UClassRegistryFrameSetBitBtnClick
          ExplicitLeft = 471
        end
        inherited RestoreBitBtn: TBitBtn
          Left = 519
          ExplicitLeft = 519
        end
      end
      inherited ListView: TListView
        Left = 283
        Height = 126
        ExplicitLeft = -122
        ExplicitTop = 43
        ExplicitHeight = 126
      end
      inherited HeaderControl: THeaderControl
        Width = 573
        ExplicitWidth = 573
      end
      inherited ComponentsListView: TListView
        Width = 283
        Height = 126
        ExplicitWidth = 283
        ExplicitHeight = 126
      end
    end
  end
end
