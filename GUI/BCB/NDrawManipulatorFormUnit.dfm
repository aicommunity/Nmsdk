object NDrawManipulatorForm: TNDrawManipulatorForm
  Left = 0
  Top = 0
  Caption = 'NDrawManipulatorForm'
  ClientHeight = 658
  ClientWidth = 691
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -14
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 120
  TextHeight = 17
  inline NDrawManipulatorFrame1: TNDrawManipulatorFrame
    Left = 0
    Top = 0
    Width = 691
    Height = 658
    Margins.Left = 4
    Margins.Top = 4
    Margins.Right = 4
    Margins.Bottom = 4
    Align = alClient
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Tahoma'
    Font.Style = []
    ParentFont = False
    TabOrder = 0
    ExplicitWidth = 691
    ExplicitHeight = 658
    inherited Panel3: TPanel
      Width = 691
      Height = 658
      Margins.Left = 4
      Margins.Top = 4
      Margins.Right = 4
      Margins.Bottom = 4
      ExplicitWidth = 691
      ExplicitHeight = 658
      inherited Image: TImage
        Width = 689
        Height = 624
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        ExplicitLeft = 1
        ExplicitTop = 1
        ExplicitWidth = 689
        ExplicitHeight = 624
      end
      inherited Button1: TButton
        Top = 625
        Width = 689
        Height = 31
        Margins.Left = 4
        Margins.Top = 4
        Margins.Right = 4
        Margins.Bottom = 4
        ExplicitTop = 625
        ExplicitWidth = 689
        ExplicitHeight = 31
      end
    end
  end
end