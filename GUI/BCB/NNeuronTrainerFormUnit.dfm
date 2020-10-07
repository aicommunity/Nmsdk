object NNeuronTrainerForm: TNNeuronTrainerForm
  Left = 0
  Top = 0
  Caption = 'NNeuronTrainerForm'
  ClientHeight = 429
  ClientWidth = 723
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
  inline NNeuronTrainerFrame1: TNNeuronTrainerFrame
    Left = 0
    Top = 0
    Width = 723
    Height = 429
    Align = alClient
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -11
    Font.Name = 'Tahoma'
    Font.Style = []
    ParentFont = False
    TabOrder = 0
    ExplicitWidth = 723
    inherited Splitter2: TSplitter
      Left = 594
      ExplicitLeft = 594
    end
    inherited ToolBar1: TToolBar
      Width = 723
      ExplicitWidth = 723
    end
    inherited StatusBar1: TStatusBar
      Width = 723
      ExplicitWidth = 723
    end
    inherited Panel2: TPanel
      Left = 602
      ExplicitLeft = 602
    end
    inherited Panel3: TPanel
      Width = 490
      ExplicitWidth = 490
      inherited Splitter3: TSplitter
        Width = 488
        ExplicitWidth = 488
      end
      inherited Panel4: TPanel
        Width = 488
        ExplicitWidth = 488
      end
      inherited Panel5: TPanel
        Width = 488
        ExplicitWidth = 488
        inherited UDrawEngineFrame1: TUDrawEngineFrame
          Width = 486
          ExplicitWidth = 486
          inherited Splitter1: TSplitter
            Left = 246
            ExplicitLeft = 246
          end
          inherited Panel1: TPanel
            Left = 257
            ExplicitLeft = 257
            inherited UClassesListFrame: TUClassesListFrame
              inherited PageControl: TPageControl
                inherited LibsControlTabSheet: TTabSheet
                  inherited Splitter1: TSplitter
                    ExplicitTop = 83
                  end
                end
              end
            end
          end
          inherited Panel2: TPanel
            Width = 246
            ExplicitWidth = 246
            inherited ScrollBox: TScrollBox
              Width = 244
              ExplicitWidth = 244
            end
          end
          inherited Panel3: TPanel
            Width = 486
            ExplicitWidth = 486
          end
        end
      end
    end
  end
end
