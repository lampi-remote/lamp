# Write a Characteristic Value

We are going to allow our iOS app to update the 'Some Number' Characteristic of our 'NumberService' and track that state locally.

## Tracking the BTLEObject State

Currently there are two properties that represent the state of our `BTLEObject` - `number` and `isConnected`. A value change to either of these properties will require that the user interface also updates. To consolidate the tracking of changes, let's combine these two values into a single **state** structure.

First we need to introduce the structure that will encapsulate the properties that represent the `BTLEObject`. Add the following to the bottom of `BTLEObject.swift`:

```swift
extension BTLEObject {
    struct State: Equatable {
        var number: Double = 0.0
        var isConnected: Bool = false
    }
}
```

By nesting our `State` structure inside a `BTLEObject`, we are effectively namespacing the type to apply to only BTLEObjects. Read [Namespacing Swift code with nested types](https://www.swiftbysundell.com/articles/namespacing-swift-code-with-nested-types/) for more information. This structure also implements the [Equitable(https://developer.apple.com/documentation/swift/equatable) protocol so we can compare it in the future.

Next, replace the `number` and `isConnected` properties with a new `state` property.

```swift
class BTLEObject: NSObject, ObservableObject {
    @Published var state: State = State()
    ...
}
```

You'll also need to update the two delegate methods that track connection to use the new `state` object:

```swift
	...
	func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
		print("Connected to peripheral: \(peripheral)")
		state.isConnected = true
	}

	func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
		print("Disconnected from peripheral: \(peripheral)")
		state.isConnected = false
	}
	...
```


If you try building now, you'll get a build error in `ContentView.swift`. This is because we removed the `number` property which was bound to our slider. Open `ContentView.swift` and update the slider to be bound to the `number` property inside our new `state` type. Also disable any interaction until the `isConnected` state is true.

```swift
struct ContentView: View {
    @ObservedObject var btleObj = BTLEObject()

    var body: some View {
        VStack {
            Slider(value:$btleObj.state.number)
            Text("Number: \(btleObj.state.number)")
        }.padding()
        .disabled(!btleObj.state.isConnected)
    }

```

## Finding a Characteristic

We need to find the 'Some Number' Characteristic so that we can write to it. Remember that a Peripheral exposes Services, and Services contain Characteristics. In the previous section, we found the peripheral in part by scanning for devices that advertised NumberService UUID.

First we need to receive input from the peripheral. Open **BTLEObject.swift** and add a new extension at the bottom to declare that it conforms to [CBPeripheralDelegate](https://developer.apple.com/reference/corebluetooth/cbperipheraldelegate) protocol:

``` swift
...

extension BTLEObject: CBPeripheralDelegate {
}
```

**NOTE:** putting so much responsibility into **BTLEObject** (`CBCentralManagerDelegate`, `CBPeripheralDelegate`, and being a model object) is poor software design - we are lumping it all in there, though to simplify the explanation.

Now we'll provide the delegate (the BTLEObject) to the Peripheral. Find the `centralManager(_:didConnect:)` function from the extension we added at the end of the previous section. Set the peripheral's delegate to `self`, and start discovery for the device service:

```swift
func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
	print("Connected to peripheral: \(peripheral)")
	state.isConnected = true
	
	peripheral.delegate = self
	peripheral.discoverServices([CBUUID(string:BTLEObject.OUR_SERVICE_UUID)])
}
```

Let's also create an optional property to store the Characteristic in **BTLEObject**:

```swift
class BTLEObject: NSObject, ObservableObject {
    ...

    private var bluetoothManager: CBCentralManager!
    private var devicePeripheral: CBPeripheral?
    private var numberCharacteristic: CBCharacteristic?

	...
}
```

Now let's implement the methods we need from [CBPeripheralDelegate](https://developer.apple.com/library/ios/documentation/CoreBluetooth/Reference/CBPeripheralDelegate_Protocol://developer.apple.com/library/ios/documentation/CoreBluetooth/Reference/CBPeripheralDelegate_Protocol/):

```swift
extension BTLEObject: CBPeripheralDelegate {
    static let SOME_NUMBER_UUID = "7a4b0001-999f-4717-b63a-066e06971f59"

	func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else { return }

        for service in services {
            print("Discovered device service")
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let characteristics = service.characteristics else { return }

        for characteristic in characteristics {
            if characteristic.uuid == CBUUID(string: BTLEObject.SOME_NUMBER_UUID) {
                print("Found characteristic with UUID: \(BTLEObject.SOME_NUMBER_UUID)")
                numberCharacteristic = characteristic
            }
        }
    }
}
```

Now build and run your app on your phone (make sure your `bleno` Bluetooth Servie is running). 

You should eventually see that the phone discovers the 'Some Number' characteristic:

![](Images/found_characteristic.png)

### Write to the Characteristic

Now let's write to the Characteristic when we change it with the slider. The 'Some Number' Characteristic takes a single byte (0 to 255). We will map the slider range (0.0 to 1.0) to that range. Thankfully Swift makes it very easy to trigger function any time our value changes. Find the `state` variable in the `BTLEObject` and add a `didSet` observer like this:

```swift
class BTLEObject: NSObject, ObservableObject {
	@Published var state: State = State(){
	    didSet {
            if state != oldValue,
               let numberCharacteristic = numberCharacteristic {

                var intToWrite = UInt8(state.number * 255.0)
                let dataToWrite = Data(bytes: &intToWrite, count: 1)
                devicePeripheral?.writeValue(dataToWrite, for: numberCharacteristic, type: .withResponse)

                print("Updated number characteristic over bluetooth")
            }
        }
	}
	...
}
```

In the `didSet`, we first check to make sure the value actually changed and then use a practice called [Optional Binding](https://docs.swift.org/swift-book/LanguageGuide/TheBasics.html#ID333) to check if the optional `numberCharacteristic` is nil or not. If the value didn't change or we do not yet have a `numberCharacteristic`, the `didSet` observer will not send data over bluetooth. 

Next, we have to convert our floating-point double value to an 8 bit integer scaled so 0.0 equal 0 and 1.0 equals 255. Finally we use this value to create a single byte [Data](https://developer.apple.com/documentation/foundation/data) object that can be written to the Characteristic, noting that we want a response from the write. Also, note that we have to unwrap the optional `devicePeripheral` with `?`. Although this property should not be `nil` at this point, unwrapping it will allow us to fail without crashing.

Since we bound this `number` property to the slider in `ContentView`, the `didSet` function will get triggered any time the slider changes this property. This is especially good since it allows us to separate responsibilities for view presentation and bluetooth communication.

Build and run the app and observe the console in Xcode. Once you see the Characteristic being found, you should be able to move the slider and see the debug output from your NodeJS Bluetooth Server respond.

## Limiting Updates
Moving the slider generates a huge number of events very quickly, far faster than our device can respond.  With a battery-powered BTLE device, that frequency of writes would use a lot of power and hurt battery life.  We can limit the update rate, while still providing a good user experience.

We'll use Apple's [Dispatch Framework](https://developer.apple.com/documentation/dispatch) is the preferred mechanism to offload computationally expensive operations using [Dispatch Queues](https://developer.apple.com/documentation/dispatch/dispatchqueue).  It has a few other uses, including running a piece of code at some point in the future. There are some subtleties with using it, including reference counting (memory management). In general, you should use weak references within a closure to long-lived objects outside the block.

Start by adding a private boolean property that defaults to `false`:

```swift
...
private var bluetoothManager: CBCentralManager!
private var devicePeripheral: CBPeripheral?
private var numberCharacteristic: CBCharacteristic?
private var updatePending: Bool = false
...
```

Then modify the `didSet`:

```swift
class BTLEObject: NSObject, ObservableObject {
    @Published var number: Double = 0.0 {
        didSet {
            if !updatePending && state != oldValue,
               let numberCharacteristic = numberCharacteristic {

                updatePending = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
                    guard let self = self else { return }

                    var intToWrite = UInt8(self.state.number * 255.0)
                    let dataToWrite = Data(bytes: &intToWrite, count: 1)
                    self.devicePeripheral?.writeValue(dataToWrite, for: numberCharacteristic, type: .withResponse)

                    self.updatePending = false

                    print("Updated number characteristic over bluetooth")
                }
            }
        }
    }
    ...
}
```

Some explanation:

* The `updatePending` flag is used to make sure we have no more than one pending update at any time.
* The `[weak self]` creates a `self` variable that is a weak and optional reference to our BTLEObject
* The `guard let self = self else { return }` allows us to perform an [Early Exit](https://docs.swift.org/swift-book/LanguageGuide/ControlFlow.html#ID525) if the optional `self` is nil. It also ensures that `self` will not be nil in the following lines.
* We need to 
* [DispatchQueue.main.asyncAfter](https://developer.apple.com/documentation/dispatch/dispatchqueue/2300100-asyncafter) delays a specified time (0.1 seconds from "now") and then executes the provided closure on the main queue. 
* We perform the Characteristic update as earlier, just that now it happens asynchronously - the weak `self` reference is captured in the closure; when the block executes, it uses the current value of the slider.
* `self` needs to now be explicitly referenced in the closure to access the `state.number` and `devicePeripheral` properties.

Run the application again - the slider should scroll smoothly and the NodeJS debug output should show less furious write activity. 

Next up: [09.7 Reading Characteristics and Notifications](../09.7_Reading_Characteristics_and_Notificiations/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
