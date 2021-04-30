# Swift and SwiftUI Essentials

### Observing an Object

In the previous section we introduced the concept of binding using the `@State` property wrapper which is great for simple value types that are owned by the view. Unfortunately it does not work for more complex types that may be modified outside of our view. 

For complex types that may contain multiple properties (*e.g., hue, saturation and brightness*) and can be modified outside of the view, we use the `@ObservedObject` property wrapper. This is what we will use to contain the Lampi state and in an upcoming chapter you'll see how this will enable SwiftUI to detect changes and update the UI without additional code. Visit Apple's documentation on [Managing Model Data in Your App](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app) for more info.

In Xcode, right click on the Project Navigator and choose **New File...** Select **Swift File** and name it **Lampi** (*the .swift extension will be automatically added.*) Click **Create** to continue. Add the following code:

```swift
class Lampi: ObservableObject {
    @Published var hue: Double = 1.0
}
```

The first line defines a Lampi class that conforms to the [ObservableObject](https://developer.apple.com/documentation/Combine/ObservableObject) protocol. The property that is wrapped by `@ObservedObject` requires its value to conform to the `ObservableObject` protocol and thus must be a class - `structs` and other primitive types cannot conform to `ObservableObject`.

The second line defines the variable `hue` and is wrapped with the `@Published`. The `@Published` property wrapper identifies `hue` as a property that when updated will emit a change notification. SwiftUI listens for that notification to automatically update views dependent on the related value - this removes the need for you to write and maintain your own synchronization code, reducing the opportunity for subtle bugs.

Replace the `myValue` variable in `LampiView` with:

```swift
@ObservedObject var lampi = Lampi()
```

This line creates a new `lampi` variable and assigns a default instance of the `Lampi` class to it. You'll notice it uses the `@ObservedObject` property wrapper. This identifies the variable as one that SwiftUI should listen to for changes and sets up the proper bindings so that we can use it for individual properties with controls like `Slider`. Since we've deleted the `myValue` property you'll need to replace the other references to it with `$lampi.hue` or `lampi.hue`.

Make these changes, build, and run the updated application on your phone.

### Adding Some Color

Obviously, color is an important aspect of Lampi and the app that controls it. Now that the `Lampi` object has a hue property, let add a calculated `color` property below `hue` that can be used in our interface.

```swift
import SwiftUI

class Lampi: ObservableObject {
    @Published var hue: Double = 1.0
    var color: Color {
        Color(hue: hue, saturation: 1.0, brightness: 1.0)
    }
	...
``` 
We're using one of the [Color](https://developer.apple.com/documentation/swiftui/color) init methods to create a SwiftUI color object using our stored hue with 100% saturation and brightness. This the color object that is returned can be used in our SwiftUI interface. In the future you will want to use the stored saturation and brightness instead of defaulting them to 100%.

You can follow this pattern and add additional computed properties to return variations of the color - perhaps a color that is always 100% saturation or brightness.

Let's now use this color in our interface by adjusting the [foregroundColor](https://developer.apple.com/documentation/swiftui/color/foregroundcolor(_:)) of the `Text` in our view. Your LampiView should now look like this:

```swift
struct LampiView: View {
    @ObservedObject var lampi = Lampi()

    var body: some View {
        VStack {
            Slider(value: $lampi.hue)
                .padding()
            Text("My Hue: \(lampi.hue)")
                .foregroundColor(lampi.color)
                .padding()
        }
    }
}
``` 

Live Preview the view and see how the color of the text changes to match the `hue` value. As the Slider changes the Lampi's `hue` value, the calculated color changes and is thus changes the text color.

There are a few different places you can set color but the two most common are [foregroundColor](https://developer.apple.com/documentation/swiftui/color/foregroundcolor(_:)) and [accentColor](https://developer.apple.com/documentation/swiftui/color/accentcolor(_:)).

### Basic SwiftUI Views

In order to complete this chapter's assignment you'll need to be familiar with some basic views that are provided by SwiftUI.

#### HStack, VStack and ZStack

[HStack](https://developer.apple.com/documentation/swiftui/hstack), [VStack](https://developer.apple.com/documentation/swiftui/vstack) and [ZStack](https://developer.apple.com/documentation/swiftui/zstack) were mentioned last section and are often basis of the layout for your other views. Be sure to read up on how to use them to align and space out views. Don't be afraid to use stacks inside of stacks.

#### Rectangle

The SwiftUI [Rectangle](https://developer.apple.com/documentation/swiftui/rectangle) is a simple as it sounds. It will fill the available space both vertically and horizontally unless you give it a specific frame size. You fill the rectangle with a color using the `fill()` view modifier. 

```swift
Rectangle()
	.fill(Color.blue)
```
#### Spacer

The [Spacer](https://developer.apple.com/documentation/swiftui/spacer) is used to fill up the available space. Using multiple spacers in a stack will result in each spacer having equal width and height.

#### Button

The SwiftUI [Button](https://developer.apple.com/documentation/swiftui/button) defines an area that can be tapped and trigger an action. Unlike other UI frameworks, `Button` can be composed of many children views including but not limited to `Text`, `Image` and any of the stack views. The size of the button will shrink to the size of its children unless you give it a specific frame size.

```swift
Button(action: {
	// Do an action or call a function
}) {
    HStack { // The HStack will stretch the button horizontally
        Spacer()
        Image(systemName: "number.circle") // Image will be centered and fill the available space
            .resizable()
            .aspectRatio(contentMode: .fit)
        Spacer()
    }.padding() // This will give some padding around the image
}
.frame(height: 100) // Limit the height of the button. Since our image is resizable it will take as much space as it can get unless we limit it.
.background(Color.blue)
.foregroundColor(.white)
```

Try adding a Button after the Text element in the view with an action that assigns the value `0.5` to `lampi.hue`.

Next up: [Assignment](../08.5_Assignment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
