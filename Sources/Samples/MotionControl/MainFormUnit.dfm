object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 
    'Engine Net Control Sample Application (c) Alexandr V. Bakhshiev,' +
    ' 2009 (www.ailab.ru)'
  ClientHeight = 555
  ClientWidth = 822
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  OldCreateOrder = False
  Position = poDesigned
  OnClose = FormClose
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 16
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 822
    Height = 100
    Margins.Left = 4
    Margins.Top = 4
    Margins.Right = 4
    Margins.Bottom = 4
    Align = alTop
    TabOrder = 0
    object Label1: TLabel
      Left = 379
      Top = 0
      Width = 113
      Height = 16
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = #1063#1080#1089#1083#1086' '#1076#1074#1080#1075'. '#1101#1083'-'#1074
    end
    object Button2: TButton
      Left = 716
      Top = 10
      Width = 93
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = #1055#1088#1086#1089#1084#1086#1090#1088
      TabOrder = 0
      Visible = False
      OnClick = Button2Click
    end
    object Button3: TButton
      Left = 15
      Top = 10
      Width = 92
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = 'Start'
      TabOrder = 1
      OnClick = Button3Click
    end
    object Button4: TButton
      Left = 114
      Top = 10
      Width = 93
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = 'Stop'
      TabOrder = 2
      OnClick = Button4Click
    end
    object Button6: TButton
      Left = 15
      Top = 57
      Width = 92
      Height = 30
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = 'Reset'
      TabOrder = 3
      OnClick = Button6Click
    end
    object CSModeRadioGroup: TRadioGroup
      Left = 214
      Top = 0
      Width = 158
      Height = 43
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = ' '#1042#1072#1088#1080#1072#1085#1090' '#1057#1059' '
      Columns = 2
      ItemIndex = 0
      Items.Strings = (
        'Full'
        'Simple')
      TabOrder = 4
      OnClick = CSModeRadioGroupClick
    end
    object LinksButton: TButton
      Left = 114
      Top = 57
      Width = 93
      Height = 30
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = #1057#1074#1103#1079#1080
      TabOrder = 5
      OnClick = LinksButtonClick
    end
    object WatchIntervalLabeledEdit: TLabeledEdit
      Left = 716
      Top = 66
      Width = 91
      Height = 24
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      EditLabel.Width = 99
      EditLabel.Height = 16
      EditLabel.Margins.Left = 4
      EditLabel.Margins.Top = 4
      EditLabel.Margins.Right = 4
      EditLabel.Margins.Bottom = 4
      EditLabel.Caption = #1053#1072#1073#1083#1102#1076#1077#1085#1080#1077', '#1089
      TabOrder = 6
      Text = '10'
    end
    object NumMotionElementsComboBox: TComboBox
      Left = 378
      Top = 16
      Width = 105
      Height = 24
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Style = csDropDownList
      ItemIndex = 0
      TabOrder = 7
      Text = '1'
      OnSelect = NumMotionElementsComboBoxSelect
      Items.Strings = (
        '1'
        '2'
        '3'
        '4'
        '5'
        '6'
        '7'
        '8'
        '9')
    end
    object MySDKIOLabeledEdit: TLabeledEdit
      Left = 565
      Top = 66
      Width = 124
      Height = 24
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      EditLabel.Width = 86
      EditLabel.Height = 16
      EditLabel.Margins.Left = 4
      EditLabel.Margins.Top = 4
      EditLabel.Margins.Right = 4
      EditLabel.Margins.Bottom = 4
      EditLabel.Caption = 'MySDK IO Buff'
      TabOrder = 8
      Text = '10'
      Visible = False
    end
    object Button1: TButton
      Left = 617
      Top = 10
      Width = 92
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = 'Test'
      TabOrder = 9
      OnClick = Button1Click
    end
    object GroupBox1: TGroupBox
      Left = 214
      Top = 43
      Width = 270
      Height = 53
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = ' '#1042#1072#1088#1080#1072#1085#1090' '#1072#1092#1092#1077#1088#1077#1085#1090#1072' '
      TabOrder = 10
      DesignSize = (
        270
        53)
      object AfferentModeComboBox: TComboBox
        Left = 10
        Top = 20
        Width = 250
        Height = 24
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        Style = csDropDownList
        Anchors = [akLeft, akTop, akRight]
        ItemIndex = 5
        TabOrder = 0
        Text = 'Branched Ind. Range Crosslinks'
        Items.Strings = (
          'Signum'
          'Range'
          'Branched Range'
          'Branched Range Crosslinks'
          'Branched Ind. Range'
          'Branched Ind. Range Crosslinks')
      end
    end
    object StatsButton: TButton
      Left = 491
      Top = 10
      Width = 92
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Caption = 'Statistic'
      TabOrder = 11
      OnClick = StatsButtonClick
    end
  end
  inline ClassRegistryFrame: TUClassRegistryFrame
    Left = 0
    Top = 100
    Width = 822
    Height = 455
    Margins.Left = 4
    Margins.Top = 4
    Margins.Right = 4
    Margins.Bottom = 4
    Align = alClient
    TabOrder = 1
    ExplicitTop = 100
    ExplicitWidth = 822
    ExplicitHeight = 455
    inherited Splitter: TSplitter
      Left = 410
      Top = 31
      Width = 4
      Height = 352
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      ExplicitLeft = 410
      ExplicitTop = 31
      ExplicitWidth = 4
      ExplicitHeight = 352
    end
    inherited Panel: TPanel
      Top = 383
      Width = 822
      Height = 72
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      ExplicitTop = 383
      ExplicitWidth = 822
      ExplicitHeight = 72
      inherited LabeledEdit: TLabeledEdit
        Left = 945
        Top = -226
        Width = 680
        Height = 24
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        EditLabel.Width = 143
        EditLabel.Height = 16
        EditLabel.Margins.Left = 4
        EditLabel.Margins.Top = 4
        EditLabel.Margins.Right = 4
        EditLabel.Margins.Bottom = 4
        EditLabel.ExplicitLeft = 945
        EditLabel.ExplicitTop = -245
        EditLabel.ExplicitWidth = 143
        EditLabel.ExplicitHeight = 16
        Text = '.........................................'
        OnKeyPress = ClassRegistryFrameLabeledEditKeyPress
        ExplicitLeft = 945
        ExplicitTop = -226
        ExplicitWidth = 680
        ExplicitHeight = 24
      end
      inherited SetBitBtn: TBitBtn
        Left = 697
        Top = 27
        Width = 51
        Height = 31
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        OnClick = ClassRegistryFrameSetBitBtnClick
        ExplicitLeft = 697
        ExplicitTop = 27
        ExplicitWidth = 51
        ExplicitHeight = 31
      end
      inherited RestoreBitBtn: TBitBtn
        Left = 756
        Top = 27
        Width = 51
        Height = 31
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        ExplicitLeft = 756
        ExplicitTop = 27
        ExplicitWidth = 51
        ExplicitHeight = 31
      end
    end
    inherited ListView: TListView
      Left = 414
      Top = 31
      Width = 408
      Height = 352
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Columns = <
        item
          Caption = 'Parameter'
          Width = 62
        end
        item
          Caption = 'Value'
          Width = 62
        end>
      Font.Height = -13
      ExplicitLeft = 414
      ExplicitTop = 31
      ExplicitWidth = 408
      ExplicitHeight = 352
    end
    inherited HeaderControl: THeaderControl
      Width = 822
      Height = 31
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      ExplicitWidth = 822
      ExplicitHeight = 31
    end
    inherited ComponentsListView: TListView
      Top = 31
      Width = 410
      Height = 352
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      Columns = <
        item
          Caption = '.. Up to previous level'
          Width = 123
        end>
      Font.Height = -13
      ExplicitTop = 31
      ExplicitWidth = 410
      ExplicitHeight = 352
    end
  end
  object Timer: TTimer
    Enabled = False
    Interval = 100
    OnTimer = TimerTimer
    Left = 16
    Top = 88
  end
  object ApplicationEvents1: TApplicationEvents
    Left = 16
    Top = 152
  end
end
