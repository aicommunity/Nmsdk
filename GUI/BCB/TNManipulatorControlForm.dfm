object NManipulatorControlForm: TNManipulatorControlForm
  Left = 0
  Top = 0
  Caption = 'NManipulatorControlForm'
  ClientHeight = 451
  ClientWidth = 693
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
    Width = 693
    Height = 29
    Caption = 'ToolBar1'
    Images = ImageList
    TabOrder = 0
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 432
    Width = 693
    Height = 19
    Panels = <>
  end
  object PageControl1: TPageControl
    Left = 0
    Top = 29
    Width = 693
    Height = 403
    ActivePage = TabSheet3
    Align = alClient
    TabOrder = 2
    object TabSheet1: TTabSheet
      Caption = 'Communication'
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object GroupBox1: TGroupBox
        Left = 0
        Top = 98
        Width = 233
        Height = 277
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
        Width = 685
        Height = 49
        Align = alTop
        Caption = ' Manipulator component name  '
        TabOrder = 1
        object ComponentSelectionPanel: TPanel
          Left = 2
          Top = 15
          Width = 681
          Height = 32
          Align = alClient
          Caption = 'Double click to select control object component '
          Color = clRed
          ParentBackground = False
          TabOrder = 0
          OnDblClick = ComponentSelectionPanelDblClick
        end
      end
      object GroupBox3: TGroupBox
        Left = 233
        Top = 98
        Width = 452
        Height = 277
        Align = alClient
        Caption = ' Communication control '
        Enabled = False
        TabOrder = 2
        DesignSize = (
          452
          277)
        object ConnectButton: TButton
          Left = 6
          Top = 20
          Width = 443
          Height = 25
          Anchors = [akLeft, akTop, akRight]
          Caption = ' Connect '
          TabOrder = 0
          OnClick = ConnectButtonClick
        end
        object DisconnectButton: TButton
          Left = 6
          Top = 51
          Width = 443
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
          Width = 443
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
          Width = 443
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
          Width = 443
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
        Width = 685
        Height = 49
        Align = alTop
        Caption = ' Control system component name  '
        TabOrder = 3
        object ControlSystemSelectionPanel: TPanel
          Left = 2
          Top = 15
          Width = 681
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
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object GroupBox4: TGroupBox
        Left = 0
        Top = 0
        Width = 185
        Height = 375
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
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 0
      ExplicitHeight = 0
      object GroupBox5: TGroupBox
        Left = 0
        Top = 0
        Width = 201
        Height = 375
        Align = alLeft
        Caption = ' External control '
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
          Left = -4
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
          Caption = 'FB by angle speed (Ia) '
          TabOrder = 4
          OnClick = IaCheckBoxClick
        end
        object IbCheckBox: TCheckBox
          Left = 5
          Top = 150
          Width = 181
          Height = 17
          Caption = 'FB by moment (Ib) '
          TabOrder = 5
          OnClick = IbCheckBoxClick
        end
        object IICheckBox: TCheckBox
          Left = 5
          Top = 170
          Width = 187
          Height = 17
          Caption = 'FB by angle (II) '
          Checked = True
          State = cbChecked
          TabOrder = 6
          OnClick = IICheckBoxClick
        end
        object ControlVoltageCheckBox: TCheckBox
          Left = 5
          Top = 208
          Width = 181
          Height = 17
          Caption = 'Control power (U) '
          Checked = True
          State = cbChecked
          TabOrder = 7
          OnClick = ControlVoltageCheckBoxClick
        end
        object GroupBox10: TGroupBox
          Left = 2
          Top = 291
          Width = 197
          Height = 82
          Align = alBottom
          Caption = ' Ext. moment '
          TabOrder = 8
          DesignSize = (
            197
            82)
          object MomentTrackBar: TTrackBar
            Left = 5
            Top = 18
            Width = 192
            Height = 27
            Anchors = [akLeft, akTop, akRight]
            Max = 1000
            Min = -1000
            TabOrder = 0
            OnChange = MomentTrackBarChange
          end
          object MomentProgressBar: TProgressBar
            Left = 13
            Top = 53
            Width = 98
            Height = 17
            Anchors = [akLeft, akTop, akRight]
            Max = 1000
            TabOrder = 1
          end
          object ExtMomentEdit: TEdit
            Left = 117
            Top = 51
            Width = 73
            Height = 21
            Anchors = [akTop, akRight]
            Color = clBtnFace
            ReadOnly = True
            TabOrder = 2
            Text = '0'
          end
        end
        object CheckBox1: TCheckBox
          Left = 5
          Top = 189
          Width = 187
          Height = 17
          Caption = 'FB by movement (Ic) '
          Checked = True
          State = cbChecked
          TabOrder = 9
          OnClick = CheckBox1Click
        end
      end
      object Panel1: TPanel
        Left = 201
        Top = 0
        Width = 484
        Height = 375
        Align = alClient
        TabOrder = 1
        object Splitter1: TSplitter
          Left = 1
          Top = 177
          Width = 482
          Height = 12
          Cursor = crVSplit
          Align = alTop
        end
        object GroupBox7: TGroupBox
          Left = 1
          Top = 1
          Width = 482
          Height = 176
          Align = alTop
          Caption = 'Control system parameters '
          TabOrder = 0
          object Label8: TLabel
            Left = 16
            Top = 67
            Width = 145
            Height = 13
            Caption = #1055#1086#1089#1090'. '#1074#1088#1077#1084#1077#1085#1080' '#1088#1072#1079#1088#1103#1076#1072' PAC:'
          end
          object Label10: TLabel
            Left = 14
            Top = 116
            Width = 85
            Height = 13
            Caption = #1052#1085#1086#1078#1080#1090#1077#1083#1100' PAC:'
          end
          object Label13: TLabel
            Left = 12
            Top = 22
            Width = 139
            Height = 13
            Caption = #1055#1086#1089#1090'. '#1074#1088#1077#1084#1077#1085#1080' '#1079#1072#1088#1103#1076#1072' PAC:'
          end
          object PACActivatorTimeTrackBar: TTrackBar
            Left = 5
            Top = 36
            Width = 141
            Height = 27
            Max = 10000
            Min = 10
            Position = 10
            TabOrder = 0
            OnChange = PACActivatorTimeTrackBarChange
          end
          object PACActivatorTimeEdit: TEdit
            Left = 144
            Top = 38
            Width = 48
            Height = 21
            TabOrder = 1
            Text = '1'
          end
          object PACDeactivatorTimeEdit: TEdit
            Left = 146
            Top = 84
            Width = 48
            Height = 21
            TabOrder = 2
            Text = '1'
          end
          object PACDeactivatorTimeTrackBar: TTrackBar
            Left = 7
            Top = 82
            Width = 141
            Height = 27
            Max = 10000
            Min = 10
            Position = 100
            TabOrder = 3
            OnChange = PACDeactivatorTimeTrackBarChange
          end
          object PACMultiplicatorTrackBar: TTrackBar
            Left = 7
            Top = 132
            Width = 141
            Height = 27
            Max = 100
            Position = 10
            TabOrder = 4
            OnChange = PACMultiplicatorTrackBarChange
          end
          object PACMultiplicatorEdit: TEdit
            Left = 146
            Top = 132
            Width = 48
            Height = 21
            TabOrder = 5
            Text = '1'
          end
          object GroupBox9: TGroupBox
            Left = 216
            Top = 15
            Width = 264
            Height = 159
            Align = alRight
            Caption = ' Visual '
            TabOrder = 6
            object Image: TImage
              Left = 2
              Top = 15
              Width = 260
              Height = 142
              Align = alClient
              AutoSize = True
              Center = True
              IncrementalDisplay = True
              Proportional = True
              Stretch = True
              ExplicitLeft = 200
              ExplicitWidth = 280
              ExplicitHeight = 159
            end
          end
        end
        object GroupBox8: TGroupBox
          Left = 1
          Top = 189
          Width = 482
          Height = 185
          Align = alClient
          Caption = ' Neuro manipulator parameters '
          TabOrder = 1
          object Label12: TLabel
            Left = 14
            Top = 106
            Width = 16
            Height = 13
            Caption = 'Va:'
          end
          object Label11: TLabel
            Left = 2
            Top = 15
            Width = 16
            Height = 13
            Align = alTop
            Caption = 'Vd:'
          end
          object Label7: TLabel
            Left = 14
            Top = 57
            Width = 97
            Height = 13
            Caption = #1042#1088#1077#1084#1103' '#1091#1087#1088#1072#1074#1083#1077#1085#1080#1103':'
          end
          object Label9: TLabel
            Left = 12
            Top = 16
            Width = 127
            Height = 13
            Caption = #1052#1085#1086#1078#1080#1090#1077#1083#1100' '#1085#1072#1087#1088#1103#1078#1077#1085#1080#1103':'
          end
          object VaEdit: TEdit
            Left = 33
            Top = 103
            Width = 48
            Height = 21
            TabOrder = 0
            Text = '100'
          end
          object VdEdit: TEdit
            Left = 111
            Top = 103
            Width = 48
            Height = 21
            TabOrder = 1
            Text = '5'
          end
          object SendVButton: TButton
            Left = 165
            Top = 101
            Width = 91
            Height = 25
            Caption = #1054#1090#1087#1088#1072#1074#1080#1090#1100
            TabOrder = 2
            OnClick = SendVButtonClick
          end
          object VoltageMulTrackBar: TTrackBar
            Left = 5
            Top = 30
            Width = 141
            Height = 27
            Max = 5000
            Position = 200
            TabOrder = 3
            OnChange = VoltageMulTrackBarChange
          end
          object TimeDurationTrackBar: TTrackBar
            Left = 5
            Top = 72
            Width = 141
            Height = 27
            Max = 256
            Min = 1
            Position = 1
            TabOrder = 4
            OnChange = TimeDurationTrackBarChange
          end
          object VoltageMulEdit: TEdit
            Left = 144
            Top = 32
            Width = 48
            Height = 21
            TabOrder = 5
            Text = '1'
          end
          object TimeDurationEdit: TEdit
            Left = 144
            Top = 74
            Width = 48
            Height = 21
            TabOrder = 6
            Text = '1'
          end
          object MulToNumberOfControlElementsCheckBox: TCheckBox
            Left = 198
            Top = 34
            Width = 50
            Height = 17
            Caption = #1087#1086' N'
            TabOrder = 7
          end
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
