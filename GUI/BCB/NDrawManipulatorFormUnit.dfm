object NDrawManipulatorForm: TNDrawManipulatorForm
  Left = 0
  Top = 0
  Caption = 'NDrawManipulatorForm'
  ClientHeight = 526
  ClientWidth = 553
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  inline NDrawManipulatorFrame1: TNDrawManipulatorFrame
    Left = 0
    Top = 0
    Width = 553
    Height = 526
    Align = alClient
    TabOrder = 0
    ExplicitLeft = 37
    ExplicitTop = -41
    inherited Panel3: TPanel
      Width = 553
      Height = 526
      ExplicitLeft = 0
      ExplicitTop = 0
      ExplicitWidth = 513
      ExplicitHeight = 382
      inherited Image: TImage
        Width = 551
        Height = 499
      end
      inherited Button1: TButton
        Top = 500
        Width = 551
        ExplicitLeft = 1
        ExplicitTop = 315
        ExplicitWidth = 548
      end
    end
  end
end
