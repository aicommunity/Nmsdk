object NManipulatorControlForm: TNManipulatorControlForm
  Left = 0
  Top = 0
  Caption = 'NManipulatorControlForm'
  ClientHeight = 434
  ClientWidth = 527
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  Menu = MainMenu
  OldCreateOrder = False
  OnClose = FormClose
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object ToolBar1: TToolBar
    Left = 0
    Top = 0
    Width = 527
    Height = 29
    Caption = 'ToolBar1'
    Images = ImageList
    TabOrder = 0
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 415
    Width = 527
    Height = 19
    Panels = <>
  end
  object PageControl1: TPageControl
    Left = 0
    Top = 29
    Width = 527
    Height = 386
    ActivePage = TabSheet3
    Align = alClient
    TabOrder = 2
    object TabSheet1: TTabSheet
      Caption = 'Communication'
      object GroupBox1: TGroupBox
        Left = 0
        Top = 98
        Width = 233
        Height = 260
        Align = alLeft
        Caption = ' Communication options '
        Enabled = False
        TabOrder = 0
        object Label1: TLabel
          Left = 7
          Top = 50
          Width = 61
          Height = 13
          Caption = 'COM port #:'
        end
        object Label2: TLabel
          Left = 18
          Top = 77
          Width = 50
          Height = 13
          Caption = 'Ctrl Mode:'
        end
        object ComPortComboBox: TComboBox
          Left = 74
          Top = 47
          Width = 151
          Height = 21
          Style = csDropDownList
          ItemIndex = 7
          TabOrder = 0
          Text = '7'
          Items.Strings = (
            '0'
            '1'
            '2'
            '3'
            '4'
            '5'
            '6'
            '7'
            '8'
            '9'
            '10'
            '11'
            '12'
            '13'
            '14'
            '15'
            '16'
            '17'
            '18'
            '19'
            '20'
            '21'
            '22'
            '23'
            '24'
            '25'
            '26'
            '27'
            '28'
            '29'
            '30')
        end
        object DeviceModeRadioButton: TRadioButton
          Left = 7
          Top = 24
          Width = 218
          Height = 17
          Caption = 'Device mode'
          Checked = True
          TabOrder = 1
          TabStop = True
          OnClick = DeviceModeRadioButtonClick
        end
        object EmulatorModeRadioButton: TRadioButton
          Left = 3
          Top = 103
          Width = 113
          Height = 17
          Caption = 'Emulator mode'
          TabOrder = 2
          OnClick = EmulatorModeRadioButtonClick
        end
        object ControlModeComboBox: TComboBox
          Left = 74
          Top = 74
          Width = 151
          Height = 21
          Style = csDropDownList
          ItemIndex = 2
          TabOrder = 3
          Text = 'Command mode'
          Items.Strings = (
            'Not set'
            'Test mode'
            'Command mode'
            'Neuro control')
        end
      end
      object GroupBox2: TGroupBox
        Left = 0
        Top = 0
        Width = 519
        Height = 49
        Align = alTop
        Caption = ' Manipulator component name  '
        TabOrder = 1
        object ComponentSelectionPanel: TPanel
          Left = 2
          Top = 15
          Width = 515
          Height = 32
          Align = alClient
          Caption = 'Double click to select manipulator component'
          Color = clRed
          ParentBackground = False
          TabOrder = 0
          OnDblClick = ComponentSelectionPanelDblClick
        end
      end
      object GroupBox3: TGroupBox
        Left = 233
        Top = 98
        Width = 286
        Height = 260
        Align = alClient
        Caption = ' Communication control '
        Enabled = False
        TabOrder = 2
        DesignSize = (
          286
          260)
        object ConnectButton: TButton
          Left = 6
          Top = 20
          Width = 277
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Connect '
          TabOrder = 0
          OnClick = ConnectButtonClick
        end
        object DisconnectButton: TButton
          Left = 6
          Top = 51
          Width = 277
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Disconnect '
          Enabled = False
          TabOrder = 1
          OnClick = DisconnectButtonClick
        end
        object ResetButton: TButton
          Left = 6
          Top = 144
          Width = 277
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Reset '
          Enabled = False
          TabOrder = 2
          OnClick = ResetButtonClick
        end
        object StartButton: TButton
          Left = 6
          Top = 82
          Width = 277
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Start '
          Enabled = False
          TabOrder = 3
          OnClick = StartButtonClick
        end
        object StopButton: TButton
          Left = 6
          Top = 113
          Width = 277
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Stop '
          Enabled = False
          TabOrder = 4
          OnClick = StopButtonClick
        end
      end
      object GroupBox6: TGroupBox
        Left = 0
        Top = 49
        Width = 519
        Height = 49
        Align = alTop
        Caption = ' Control system component name  '
        TabOrder = 3
        object ControlSystemSelectionPanel: TPanel
          Left = 2
          Top = 15
          Width = 515
          Height = 32
          Align = alClient
          Caption = 'Double click to select control system'
          Color = clRed
          ParentBackground = False
          TabOrder = 0
          OnDblClick = ControlSystemSelectionPanelDblClick
        end
      end
    end
    object TabSheet2: TTabSheet
      Caption = 'Manual Control'
      ImageIndex = 1
      object GroupBox4: TGroupBox
        Left = 0
        Top = 0
        Width = 185
        Height = 358
        Align = alLeft
        Caption = ' Servo Control '
        TabOrder = 0
        object Время: TLabel
          Left = 8
          Top = 120
          Width = 22
          Height = 13
          Caption = 'Time'
        end
        object Скорость: TLabel
          Left = 8
          Top = 65
          Width = 30
          Height = 13
          Caption = 'Speed'
        end
        object Label3: TLabel
          Left = 55
          Top = 19
          Width = 42
          Height = 13
          Caption = 'Direction'
        end
        object Label4: TLabel
          Left = 7
          Top = 19
          Width = 39
          Height = 13
          Caption = 'Servo #'
        end
        object Button2: TButton
          Left = 4
          Top = 175
          Width = 171
          Height = 25
          Caption = 'Move'
          TabOrder = 0
          OnClick = Button2Click
        end
        object TrackBarTime: TTrackBar
          Left = 0
          Top = 136
          Width = 182
          Height = 33
          Max = 255
          Frequency = 8
          Position = 32
          TabOrder = 1
        end
        object TrackBarPWM: TTrackBar
          Left = 0
          Top = 81
          Width = 182
          Height = 33
          Max = 255
          Frequency = 8
          Position = 128
          TabOrder = 2
        end
        object ComboBoxDir: TComboBox
          Left = 55
          Top = 38
          Width = 119
          Height = 21
          Style = csDropDownList
          ItemIndex = 0
          TabOrder = 3
          Text = 'CV'
          Items.Strings = (
            'CV'
            'CCV')
        end
        object CBoxServoMove: TComboBox
          Left = 7
          Top = 38
          Width = 41
          Height = 21
          Style = csDropDownList
          ItemIndex = 0
          TabOrder = 4
          Text = '0'
          Items.Strings = (
            '0'
            '1')
        end
      end
    end
    object TabSheet3: TTabSheet
      Caption = 'Neuro Control'
      ImageIndex = 2
      object GroupBox5: TGroupBox
        Left = 0
        Top = 0
        Width = 201
        Height = 358
        Align = alLeft
        Caption = ' '#1042#1085#1077#1096#1085#1077#1077' '#1091#1087#1088#1072#1074#1083#1077#1085#1080#1077' '
        TabOrder = 0
        object Label5: TLabel
          Left = 12
          Top = 18
          Width = 163
          Height = 13
          Caption = 'II Afferent ext. control frequency'
        end
        object Label6: TLabel
          Left = 12
          Top = 77
          Width = 174
          Height = 13
          Caption = 'Number of II Afferents ext. controls'
        end
        object IIAfferentTrackBar: TTrackBar
          Left = 2
          Top = 37
          Width = 146
          Height = 27
          Max = 200
          Min = -200
          TabOrder = 0
          OnChange = IIAfferentTrackBarChange
        end
        object IIAfferentEdit: TEdit
          Left = 148
          Top = 37
          Width = 44
          Height = 21
          Color = clBtnFace
          ReadOnly = True
          TabOrder = 1
          Text = '0'
        end
        object IINumAfferentTrackBar: TTrackBar
          Left = 2
          Top = 93
          Width = 146
          Height = 27
          Max = 5
          TabOrder = 2
          OnChange = IINumAfferentTrackBarChange
        end
        object IINumAfferentEdit: TEdit
          Left = 148
          Top = 93
          Width = 44
          Height = 21
          Color = clBtnFace
          ReadOnly = True
          TabOrder = 3
          Text = '0'
        end
        object IaCheckBox: TCheckBox
          Left = 5
          Top = 128
          Width = 181
          Height = 17
          Caption = #1054#1057' '#1087#1086' '#1091#1075#1083#1086#1074#1086#1081' '#1089#1082#1086#1088#1086#1089#1090#1080' (Ia) '
          Checked = True
          State = cbChecked
          TabOrder = 4
          OnClick = IaCheckBoxClick
        end
        object IbCheckBox: TCheckBox
          Left = 5
          Top = 150
          Width = 181
          Height = 17
          Caption = #1054#1057' '#1087#1086' '#1082#1088#1091#1090#1103#1097#1077#1084#1091' '#1084#1086#1084#1077#1085#1090#1091' (Ib) '
          TabOrder = 5
          OnClick = IbCheckBoxClick
        end
        object IICheckBox: TCheckBox
          Left = 5
          Top = 170
          Width = 187
          Height = 17
          Caption = #1054#1057' '#1087#1086' '#1091#1075#1083#1091' (II) '
          Checked = True
          State = cbChecked
          TabOrder = 6
          OnClick = IICheckBoxClick
        end
        object ControlVoltageCheckBox: TCheckBox
          Left = 5
          Top = 193
          Width = 181
          Height = 17
          Caption = #1059#1087#1088#1072#1074#1083#1103#1102#1097#1077#1077' '#1074#1086#1079#1076#1077#1081#1089#1090#1074#1080#1077' (U) '
          Checked = True
          State = cbChecked
          TabOrder = 7
          OnClick = ControlVoltageCheckBoxClick
        end
        object RadioGroup1: TRadioGroup
          Left = 2
          Top = 296
          Width = 197
          Height = 60
          Align = alBottom
          Caption = ' '#1054#1059
          ItemIndex = 0
          Items.Strings = (
            #1052#1086#1076#1077#1083#1100
            #1052#1072#1085#1080#1087#1091#1083#1103#1090#1086#1088)
          TabOrder = 8
          OnClick = RadioGroup1Click
        end
      end
    end
  end
  object ImageList: TImageList
    Left = 464
    Top = 40
  end
  object MainMenu: TMainMenu
    Left = 408
    Top = 40
    object Communication1: TMenuItem
      Caption = 'Communication'
      object SelectManipulator1: TMenuItem
        Caption = 'Select Manipulator'
        OnClick = SelectManipulator1Click
      end
      object SelectControlSystem1: TMenuItem
        Caption = 'Select Control System'
        OnClick = SelectControlSystem1Click
      end
      object N1: TMenuItem
        Caption = '-'
      end
      object Connect1: TMenuItem
        Caption = 'Connect'
        OnClick = Connect1Click
      end
      object Disconnect1: TMenuItem
        Caption = 'Disconnect'
        OnClick = Disconnect1Click
      end
      object Start1: TMenuItem
        Caption = 'Start'
        OnClick = Start1Click
      end
      object Stop1: TMenuItem
        Caption = 'Stop'
        OnClick = Stop1Click
      end
      object Reset1: TMenuItem
        Caption = 'Reset'
        OnClick = Reset1Click
      end
    end
    object Move1: TMenuItem
      Caption = 'Move'
      object MoveLeft1: TMenuItem
        Caption = 'Move Left'
        OnClick = MoveLeft1Click
      end
      object MoveRight1: TMenuItem
        Caption = 'Move Right'
        OnClick = MoveRight1Click
      end
    end
  end
end
