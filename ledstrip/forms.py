# -*- coding: utf-8 -*-
from django import forms
import glob


LED_effect_choices = [('off',     'Off'),
                      ('rainbow', 'Rainbow'),
                      ('blink',   'Blink'),
                      ('moving',  'Moving')]

music_choices = [('off', 'No music')]
file_list = glob.glob("/home/pi/music/*.mp3")
for filepath in file_list:
    music_choices.append((filepath, filepath.split('/')[-1]))

class ChristmasTree(forms.Form):
    LED_effect = forms.ChoiceField(choices=LED_effect_choices, widget=forms.RadioSelect(choices=LED_effect_choices), required=False)
    music = forms.ChoiceField(choices=music_choices, widget=forms.RadioSelect(choices=music_choices), required=False)
    volume = forms.IntegerField(min_value=0, max_value=100, required=False, help_text='between 0 and 100%')

#####################################################################################
blind_music_choices = [('off', 'No music')]
file_list = glob.glob("/home/pi/music/blind_test/*.mp3")
for filepath in file_list:
    blind_music_choices.append((filepath, filepath.split('/')[-1]))
team_choice = [('blue', 'Blue team'), ('red', 'Red team')]
team_reset_choice = [('blue', 'Blue team'), ('red', 'Red team'), ('reset', 'Reset')]

class BlindMaster(forms.Form):
    blind_music = forms.ChoiceField(choices=blind_music_choices, widget=forms.RadioSelect(choices=music_choices), required=False)
    volume = forms.IntegerField(min_value=0, max_value=100, required=False, help_text='between 0 and 100%')
    add_point = forms.ChoiceField(choices=team_choice, widget=forms.RadioSelect(choices=team_choice), required=False)
    remove_point = forms.ChoiceField(choices=team_reset_choice, widget=forms.RadioSelect(choices=team_reset_choice), required=False)
    bad_answer_continue = forms.BooleanField(required=False)

class BlindTeam(forms.Form):
    pass