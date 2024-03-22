import ipywidgets as widgets
class EditableDictionaryDisplay:
    def __init__(self, dictionary):
        self._dictionary = dictionary
        self._output = widgets.Output()
        self._edit_button = widgets.Button(description="Edit")
        self._edit_button.on_click(self._toggle_editable)
        self._editable = False
        self._editable_widgets = {}
        self.grid = None
        
    def display(self):
        self._refresh_output()
        self.grid = widgets.GridBox([self._output, widgets.HBox([self._edit_button])], layout=widgets.Layout(grid_template_rows="1fr 1fr"))
        display(self.grid)


    def _refresh_output(self):
        self._output.clear_output()
        with self._output:
            for key, value in self._dictionary.items():
                print(f"{key}: {value}")

    def _toggle_editable(self,_):
        if self._editable:
            self._update_dictionary()
            self._refresh_output()
            self._edit_button.description = "Edit"
            self._editable = False
            for widget in self._editable_widgets.values():
              widget.close()
        else:
            self._create_editable_widgets()
            self._edit_button.description = "Save"
            self._editable = True

    def _create_editable_widgets(self):
      self._output.clear_output()
      self._editable_widgets = {}  
      widgets_list = [self._output, widgets.HBox([self._edit_button])]
      for key, value in self._dictionary.items():
          self._editable_widgets[key] = widgets.Text(value=str(value), description=key)
          widgets_list += (self._editable_widgets[key],)
      self.grid.children = widgets_list
      display(self.grid)

    def _update_dictionary(self):
        for key, widget in self._editable_widgets.items():
            self._dictionary[key] = widget.value

    def return_values(self) -> dict:
      return self._dictionary